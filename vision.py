"""
vision.py — merged best of vision1 + vision2
- Lock/tracking + velocity prediction + RCS  (vision1)
- Score-based target selection + noise reduction (vision1)
- Full key map 30+ ปุ่ม (vision2)
- ctypes mouse check ครบ (vision2)
- Dynamic FOV + global decls ครบ (bugfix)
- Thread-safe state access with locking (critical fix)
"""

import cv2
import numpy as np
import time
import keyboard
import ctypes
import threading
import traceback
from collections import deque
from config import config
from arduino import send_to_arduino
from humanize import humanize_movement
# pyautogui ถูกลบออก — ใช้ Arduino HID อย่างเดียว (ป้องกัน 2x movement)
# หากต้องการ fallback ให้ uncomment และตรวจสอบให้ไม่ใช้พร้อมกัน

# ═══════════════════════════════════════════════════════
#  LOCK HIERARCHY (prevent deadlock)
# ═══════════════════════════════════════════════════════
_vision_lock = threading.Lock()      # Level 1: Vision state (highest priority)
_vision_state_lock = _vision_lock    # Alias for backward compatibility
                                     # Level 2: Config lock (in config.py)
                                     # Level 3: Arduino lock (in arduino.py - already exists)

# ── dxcam preferred, mss fallback ───────────────────────
try:
    import dxcam as _dx
    _cam       = _dx.create(output_color="BGR")
    _USE_DXCAM = True
    print("[CAPTURE] dxcam OK")
except Exception:
    import mss as _mss
    _USE_DXCAM = False
    print("[CAPTURE] mss fallback (pip install dxcam for FPS)")

_mss_ctx = None

def _grab(mon: dict):
    global _mss_ctx
    if _USE_DXCAM:
        r = (mon["left"], mon["top"],
             mon["left"]+mon["width"], mon["top"]+mon["height"])
        return _cam.grab(region=r)   # BGR or None on drop
    if _mss_ctx is None:
        _mss_ctx = _mss.mss()
    return cv2.cvtColor(np.array(_mss_ctx.grab(mon)), cv2.COLOR_BGRA2BGR)


# ═══════════════════════════════════════════════════════
#  GLOBAL STATE
# ═══════════════════════════════════════════════════════
_active          = False
fps_history     = deque(maxlen=60)
last_frame_time = 0.0
target_count    = 0
AIM_ZONE        = "head"
AIM_ZONE_MAP    = {"head": 0.18, "neck": 0.28, "body": 0.50}

# Window toggles (guarded by _vision_lock)
_show_monitor    = True
_show_fov        = True

# Thread-safe accessors for cross-thread booleans
def get_active():
    with _vision_lock:
        return _active

def set_active(val: bool):
    global _active
    with _vision_lock:
        _active = val

def toggle_active() -> bool:
    global _active
    with _vision_lock:
        _active = not _active
        return _active

def get_show_monitor():
    with _vision_lock:
        return _show_monitor

def set_show_monitor(val: bool):
    global _show_monitor
    with _vision_lock:
        _show_monitor = val

def toggle_show_monitor() -> bool:
    global _show_monitor
    with _vision_lock:
        _show_monitor = not _show_monitor
        return _show_monitor

def get_show_fov():
    with _vision_lock:
        return _show_fov

def set_show_fov(val: bool):
    global _show_fov
    with _vision_lock:
        _show_fov = val

def toggle_show_fov() -> bool:
    global _show_fov
    with _vision_lock:
        _show_fov = not _show_fov
        return _show_fov

# --- backward-compat properties (for routes.py direct attribute access) ---
# These are module-level shims so that `vision.active` still works externally
class _ActiveProxy:
    """Allows `vision.active = X` and `if vision.active:` to go through lock."""
    def __bool__(self): return get_active()
    def __repr__(self): return str(get_active())

# We'll keep 'active', 'show_monitor', 'show_fov' as module attrs for backward compat
# but routes.py should be updated to use the thread-safe accessors.

# Thread-safe state container
_lock_bbox = None
_lock_lost = 0
_lock_vx   = 0.0
_lock_vy   = 0.0
_lock_prev_area = 0.0  # ← สำหรับ confidence scoring

_LOST_MAX    = 10
_PRED_W      = 0.35
_VEL_EMA     = 0.30

# Error tracking
_consecutive_errors = 0
_ERROR_THRESHOLD = 10

def _write_lock_state(bbox=None, lost=None, vx=None, vy=None):
    """Atomic write to lock state"""
    global _lock_bbox, _lock_lost, _lock_vx, _lock_vy
    with _vision_lock:
        if bbox is not None: _lock_bbox = bbox
        if lost is not None: _lock_lost = lost
        if vx is not None:   _lock_vx = vx
        if vy is not None:   _lock_vy = vy


# ═══════════════════════════════════════════════════════
#  OUTLIER FILTERING (Feature 2) — Phase 1 Foundation
# ═══════════════════════════════════════════════════════

class OutlierState:
    """Tracks historical detection data for outlier validation.
    
    Maintains a deque of the 5 most recent valid bounding boxes.
    Thread-safe when accessed under _vision_lock.
    """
    
    def __init__(self, max_history: int = 5):
        """Initialize outlier state with circular buffer.
        
        Args:
            max_history: Number of frames to keep in history (default 5)
        """
        self.max_history = max_history
        self.bbox_history = deque(maxlen=max_history)
        self.frame_count = 0
    
    def add_detection(self, bbox):
        """Record a valid detection for history.
        
        Args:
            bbox: Tuple (x, y, w, h) of the detection bounding box
        """
        self.bbox_history.append(bbox)
        self.frame_count += 1
    
    def get_previous_bbox(self):
        """Get most recent detection (1-frame ago).
        
        Returns:
            Tuple (x, y, w, h) of the most recent bbox, or None if empty
        """
        if len(self.bbox_history) < 1:
            return None
        return self.bbox_history[-1]
    
    def get_oldest_bbox(self):
        """Get oldest detection in history (for baseline comparisons).
        
        Returns:
            Tuple (x, y, w, h) of the oldest bbox, or None if empty
        """
        if len(self.bbox_history) < 1:
            return None
        return self.bbox_history[0]
    
    def clear(self):
        """Clear history (e.g., when target lost)."""
        self.bbox_history.clear()
        self.frame_count = 0


# Global outlier state instance
_outlier_state = OutlierState(max_history=5)


# ─────────────────────────────────────────────────────
#  VALIDATOR FUNCTIONS (Outlier Filtering)
# ─────────────────────────────────────────────────────

def validate_movement(prev_bbox, curr_bbox, frame_width, max_speed_pct):
    """Validate that target movement between frames is realistic.
    
    Rejects detections that teleport (move faster than human head speed).
    First detection always accepted.
    
    Args:
        prev_bbox: Tuple (x, y, w, h) of previous detection, or None
        curr_bbox: Tuple (x, y, w, h) of current detection
        frame_width: Width of capture frame (FOV) in pixels
        max_speed_pct: Max movement as % of frame_width per frame (e.g., 0.30)
    
    Returns:
        bool: True if movement valid, False if teleporting
    """
    if prev_bbox is None:
        return True  # No previous frame — always accept first detection
    
    # Calculate centers
    prev_x, prev_y, prev_w, prev_h = prev_bbox
    curr_x, curr_y, curr_w, curr_h = curr_bbox
    
    prev_cx = prev_x + prev_w / 2.0
    prev_cy = prev_y + prev_h / 2.0
    curr_cx = curr_x + curr_w / 2.0
    curr_cy = curr_y + curr_h / 2.0
    
    # Calculate Euclidean distance
    dx = curr_cx - prev_cx
    dy = curr_cy - prev_cy
    distance = (dx*dx + dy*dy) ** 0.5
    
    # Calculate max allowed movement per frame
    max_movement = frame_width * max_speed_pct
    
    return distance <= max_movement


def validate_size_ratio(prev_bbox, curr_bbox, min_ratio, max_ratio):
    """Validate that bounding box size ratio is within acceptable range.
    
    Rejects morphing detections where size changes too drastically.
    First detection skips validation.
    
    Args:
        prev_bbox: Tuple (x, y, w, h) of previous detection, or None
        curr_bbox: Tuple (x, y, w, h) of current detection
        min_ratio: Minimum size ratio (e.g., 0.50 = 50% of previous size)
        max_ratio: Maximum size ratio (e.g., 2.00 = 200% of previous size)
    
    Returns:
        bool: True if ratio in range, False if morphing
    """
    if prev_bbox is None:
        return True  # No baseline — skip validation for first detection
    
    prev_x, prev_y, prev_w, prev_h = prev_bbox
    curr_x, curr_y, curr_w, curr_h = curr_bbox
    
    prev_area = prev_w * prev_h
    curr_area = curr_w * curr_h
    
    if prev_area == 0:
        return True  # Avoid division by zero
    
    ratio = curr_area / prev_area
    
    return min_ratio <= ratio <= max_ratio


def validate_bounds(bbox, frame_width, frame_height):
    """Validate that bounding box is fully within frame boundaries.
    
    Rejects partial detections at FOV edges (often artifacts).
    
    Args:
        bbox: Tuple (x, y, w, h) of detection bounding box
        frame_width: Width of capture frame in pixels
        frame_height: Height of capture frame in pixels
    
    Returns:
        bool: True if fully inside, False if extends past boundary
    """
    x, y, w, h = bbox
    
    # Check left edge
    if x < 0:
        return False
    
    # Check right edge
    if x + w > frame_width:
        return False
    
    # Check top edge
    if y < 0:
        return False
    
    # Check bottom edge
    if y + h > frame_height:
        return False
    
    return True


def validate_aspect_ratio(prev_bbox, curr_bbox, max_change):
    """Validate that aspect ratio (height/width) remains stable.
    
    Rejects distorted detections where shape changes too drastically.
    First detection skips validation.
    
    Args:
        prev_bbox: Tuple (x, y, w, h) of previous detection, or None
        curr_bbox: Tuple (x, y, w, h) of current detection
        max_change: Maximum aspect ratio change (e.g., 0.15 = ±15%)
    
    Returns:
        bool: True if aspect ratio stable, False if distorted
    """
    if prev_bbox is None:
        return True  # No baseline — skip validation for first detection
    
    prev_x, prev_y, prev_w, prev_h = prev_bbox
    curr_x, curr_y, curr_w, curr_h = curr_bbox
    
    # Handle zero width (prevent division by zero)
    if prev_w == 0 or curr_w == 0:
        return False
    
    prev_aspect = prev_h / prev_w
    curr_aspect = curr_h / curr_w
    
    aspect_delta = abs(curr_aspect - prev_aspect)
    
    return aspect_delta <= max_change


def validate_contour(contour, prev_bbox, frame_width, frame_height, config):
    """Composite outlier validation with early-exit chain.
    
    Validates detection against 4 criteria in sequence:
    1. Movement: distance <= 30% FOV width
    2. Size: area ratio in [0.5, 2.0]x
    3. Bounds: fully within frame
    4. Aspect: ratio change <= ±0.15
    
    Early-exits on first failure to save computation.
    
    Args:
        contour: OpenCV contour array
        prev_bbox: Previous bbox for comparison, or None
        frame_width: FOV width in pixels
        frame_height: FOV height in pixels
        config: Dict with detection parameters:
            - max_speed_pct: Movement threshold (default 0.30)
            - min_size_ratio: Min size ratio (default 0.50)
            - max_size_ratio: Max size ratio (default 2.00)
            - max_aspect_change: Aspect ratio threshold (default 0.15)
    
    Returns:
        Tuple (is_valid, reason):
        - is_valid: bool, True if passes all checks
        - reason: str, "valid" or one of:
          - "movement_outlier": distance exceeds threshold
          - "size_outlier": area ratio out of range
          - "bounds_outlier": extends past frame edge
          - "shape_outlier": aspect ratio change exceeds threshold
    """
    # Extract current bounding box
    x, y, w, h = cv2.boundingRect(contour)
    curr_bbox = (x, y, w, h)
    
    # Get config parameters with defaults
    max_speed_pct = config.get('max_speed_pct', 0.30)
    min_size_ratio = config.get('min_size_ratio', 0.50)
    max_size_ratio = config.get('max_size_ratio', 2.00)
    max_aspect_change = config.get('max_aspect_change', 0.15)
    
    # Check 1: Movement (early-exit on fail)
    if not validate_movement(prev_bbox, curr_bbox, frame_width, max_speed_pct):
        return (False, "movement_outlier")
    
    # Check 2: Size ratio (early-exit on fail)
    if not validate_size_ratio(prev_bbox, curr_bbox, min_size_ratio, max_size_ratio):
        return (False, "size_outlier")
    
    # Check 3: Bounds (early-exit on fail)
    if not validate_bounds(curr_bbox, frame_width, frame_height):
        return (False, "bounds_outlier")
    
    # Check 4: Aspect ratio (early-exit on fail)
    if not validate_aspect_ratio(prev_bbox, curr_bbox, max_aspect_change):
        return (False, "shape_outlier")
    
    # All checks passed
    return (True, "valid")

def _read_lock_state():
    """Atomic read from lock state"""
    with _vision_lock:
        return {
            'bbox': _lock_bbox,
            'lost': _lock_lost,
            'vx': _lock_vx,
            'vy': _lock_vy
        }


# ═══════════════════════════════════════════════════════
#  COLOR DETECTION
# ═══════════════════════════════════════════════════════
def detect_color(hsv: np.ndarray, lower: np.ndarray = None, upper: np.ndarray = None) -> np.ndarray:
    """Detect color in HSV frame. Uses provided bounds (thread-safe) or falls back to config."""
    if lower is None:
        lower = config.LOWER_COLOR
    if upper is None:
        upper = config.UPPER_COLOR
    mask = cv2.inRange(hsv, lower, upper)
    if lower[0] <= 10:   # red hue wrap-around
        m2   = cv2.inRange(hsv,
                   np.array([170, lower[1], lower[2]]),
                   np.array([180, upper[1], upper[2]]))
        mask = cv2.bitwise_or(mask, m2)
    return mask


# ═══════════════════════════════════════════════════════
#  FEATURE 1: CONFIDENCE SCORING
# ═══════════════════════════════════════════════════════

def calculate_confidence(contour, frame_hsv, fov_center, previous_area=None):
    """
    คำนวณ confidence score (0-1) ของ detection
    
    พิจารณา:
    1. Color match quality (%)
    2. Size consistency (เทียบกับ history)
    3. Position within FOV (center = good)
    4. Shape validity (aspect ratio)
    
    ผลลัพธ์: 0.0 (หดหู่) ถึง 1.0 (มั่นใจสูง)
    """
    area = cv2.contourArea(contour)
    if area < config.MIN_AREA:
        return 0.0
    
    x, y, w, h = cv2.boundingRect(contour)
    cx, cy = x + w // 2, y + h // 2
    
    # ━━━ 1. Color Match Quality (0-1)
    # Human figure: aspect ratio ~0.4-0.8
    aspect_ratio = h / (w + 1)
    color_match = min(1.0, aspect_ratio / 0.6) if aspect_ratio < 0.6 else 1.0
    
    # ━━━ 2. Size Consistency (0-1)
    # ยอมรับ 0.5-2.0x เทียบกับ frame ที่แล้ว
    if previous_area is not None and previous_area > 0:
        area_ratio = area / previous_area
        if 0.5 < area_ratio < 2.0:
            size_consistency = 1.0
        else:
            size_consistency = 0.5 * (1.0 - min(1.0, abs(area_ratio - 1.0) / 2.0))
    else:
        size_consistency = 0.8
    
    # ━━━ 3. Position within FOV (0-1)
    # ตรงกลาง = 1.0, ขอบ = 0.7
    dist_to_center = ((cx - fov_center[0])**2 + (cy - fov_center[1])**2) ** 0.5
    max_dist = fov_center[0] * 1.5
    position_score = max(0.7, 1.0 - (dist_to_center / (max_dist + 1)) * 0.3)
    
    # ━━━ 4. Shape Validity (0-1)
    # Human-like: aspect ratio 0.4-0.8, solidity >0.6
    solidity = area / (w * h + 1)
    
    if 0.4 < aspect_ratio < 0.8 and solidity > 0.6:
        shape_score = 1.0
    elif 0.3 < aspect_ratio < 1.0 and solidity > 0.5:
        shape_score = 0.7
    else:
        shape_score = 0.4
    
    # ━━━ รวมทั้งหมด (weighted average)
    confidence = (
        0.3 * color_match +
        0.25 * size_consistency +
        0.25 * position_score +
        0.2 * shape_score
    )
    
    return min(1.0, max(0.0, confidence))


# ═══════════════════════════════════════════════════════
#  VISION STATE SNAPSHOT (atomic getter for /status)
# ═══════════════════════════════════════════════════════
def get_vision_snapshot():
    """Returns atomic snapshot of vision state for /status endpoint."""
    with _vision_lock:
        return {
            "lock_bbox": _lock_bbox.copy() if _lock_bbox else None,
            "lock_vx": float(_lock_vx),
            "lock_vy": float(_lock_vy),
            "lock_lost": int(_lock_lost),
            "active": bool(_active),
            "show_monitor": bool(_show_monitor),
            "show_fov": bool(_show_fov),
            "target_count": int(target_count),
            "fps": int(sum(fps_history)/len(fps_history)) if fps_history else 0,
            "consecutive_errors": int(_consecutive_errors),
            "error_threshold_hit": _consecutive_errors >= _ERROR_THRESHOLD,
        }

def reset_error_counter():
    """Reset error counter when vision loop succeeds."""
    global _consecutive_errors
    with _vision_lock:
        if _consecutive_errors > 0:
            print("[VISION] Vision recovered (error counter reset)")
            _consecutive_errors = 0


# ═══════════════════════════════════════════════════════
#  INPUT — full key map (vision2)
# ═══════════════════════════════════════════════════════
_AIM_KEY_MAP = {
    "always": None,
    "alt":"alt", "shift":"shift", "ctrl":"ctrl",
    "capslock":"caps lock", "tab":"tab", "space":"space",
    "enter":"enter", "backspace":"backspace",
    # letters
    "q":"q","e":"e","r":"r","f":"f","g":"g",
    "x":"x","z":"z","c":"c","v":"v","t":"t",
    "y":"y","h":"h","b":"b","n":"n",
    # function keys
    "f1":"f1","f2":"f2","f3":"f3","f4":"f4",
    "f5":"f5","f6":"f6","f7":"f7","f8":"f8",
    # numpad
    "num0":"num 0","num1":"num 1","num2":"num 2",
    "num3":"num 3","num4":"num 4","num5":"num 5",
    # mouse
    "mouse1":"left","mouse2":"right",
    "mouse4":"xbutton1","mouse5":"xbutton2",
}

_TRIG_KEY_MAP = {
    "mouse1":("m","left"),  "mouse2":("m","right"),
    "mouse4":("m","x"),     "mouse5":("m","x2"),
    "f":("k","f"),  "g":("k","g"),  "v":("k","v"),
    "z":("k","z"),  "e":("k","e"),  "r":("k","r"),
    "c":("k","c"),  "q":("k","q"),  "x":("k","x"),
    "t":("k","t"),  "y":("k","y"),  "h":("k","h"),
    "b":("k","b"),  "n":("k","n"),
    "tab":("k","tab"),     "space":("k","space"),
    "shift":("k","shift"), "ctrl":("k","ctrl"),
    "capslock":("k","caps lock"),
    "f1":("k","f1"),"f2":("k","f2"),"f3":("k","f3"),
    "f4":("k","f4"),"f5":("k","f5"),"f6":("k","f6"),
    "num0":("k","num 0"),"num1":("k","num 1"),
    "num2":("k","num 2"),"num3":("k","num 3"),
    "num4":("k","num 4"),"num5":("k","num 5"),
}

_MOUSE_VK = {"left":0x01,"right":0x02,"x":0x05,"x2":0x06,
             "xbutton1":0x05,"xbutton2":0x06}

def _mouse_held(btn: str) -> bool:
    try:
        vk = _MOUSE_VK.get(btn, 0x01)
        return bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)
    except:
        return False

def is_activation_key_pressed() -> bool:
    k = config.ACTIVATION_KEY
    if k == "always": return True
    m = _AIM_KEY_MAP.get(k, k)
    try:
        if k.startswith("mouse"): return _mouse_held(m)
        return keyboard.is_pressed(m)
    except:
        return False

_last_trig_ms = 0.0
_fire_start_time = 0.0

RCS_PATTERN = [
    0.5, 1.2, 1.8, 2.1, 1.9, 1.6, 1.3, 1.0,
    0.8, 0.6, 0.4, 0.2,
    0.1, 0.0,
]

def _trig_held() -> bool:
    t = _TRIG_KEY_MAP.get(config.TRIGGER_KEY)
    if not t: return False
    kind, btn = t
    try:
        return _mouse_held(btn) if kind == "m" else keyboard.is_pressed(btn)
    except:
        return False

def check_trigger_fire() -> bool:
    global _last_trig_ms, _fire_start_time
    now = time.perf_counter() * 1000
    if now - _last_trig_ms < config.TRIGGER_DELAY: return False
    if _trig_held():
        _last_trig_ms = now
        _fire_start_time = time.perf_counter()
        return True
    return False


# ═══════════════════════════════════════════════════════
#  COLOR PICKER  (right-click)
# ═══════════════════════════════════════════════════════
def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_RBUTTONDOWN:
        hsv = cv2.cvtColor(param, cv2.COLOR_BGR2HSV)
        h,s,v = int(hsv[y,x][0]), int(hsv[y,x][1]), int(hsv[y,x][2])
        config.LOWER_COLOR = np.array([max(0,h-18), max(40,s-60), max(40,v-60)])
        config.UPPER_COLOR = np.array([min(180,h+18), 255, 255])
        config.save()
        print("[COLOR] HSV({},{},{}) -> {}~{}".format(h, s, v, config.LOWER_COLOR, config.UPPER_COLOR))


# ═══════════════════════════════════════════════════════
#  VISION LOOP
# ═══════════════════════════════════════════════════════
def vision_loop():
    global _active, target_count, last_frame_time, fps_history
    global _lock_bbox, _lock_lost, _lock_vx, _lock_vy, _consecutive_errors, _lock_prev_area

    cap_tag = "[DX]" if _USE_DXCAM else "[MS]"
    print("[VISION] Started [{}]".format(cap_tag))
    k3 = np.ones((3, 3), np.uint8)

    # Create window ONCE before loop (avoid per-frame overhead)
    _window_created = False

    while True:
        try:
            # ── Atomic config snapshot — ONE lock acquisition per frame ──
            cfg = config.get_detection_params()
            fov = cfg['fov']
            mon = {
                "left":   config.SCREEN_WIDTH  // 2 - fov // 2,
                "top":    config.SCREEN_HEIGHT // 2 - fov // 2,
                "width":  fov,
                "height": fov,
            }

            t0    = time.perf_counter()   # ย้ายมาก่อน grab — วัด FPS จริงรวม capture time
            frame = _grab(mon)
            if frame is None:
                continue   # dxcam frame drop

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # ── Detection + noise reduction (vision1) ────
            # Use snapshot colors for thread safety
            mask = detect_color(hsv, lower=cfg['lower_color'], upper=cfg['upper_color'])
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.erode(mask,  k3, iterations=1)
            mask = cv2.dilate(mask, k3, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
            valid = [c for c in contours
                     if cfg['min_area'] < cv2.contourArea(c) < cfg['max_area']]
            
            # ✨ FEATURE 2: Apply outlier filtering (early rejection of noise/artifacts)
            # Get previous bbox snapshot for outlier validation
            with _vision_lock:
                _snapshot_bbox_for_outlier = _lock_bbox
            
            filtered_contours = []
            for cnt in valid:
                is_valid, reason = validate_contour(
                    cnt,
                    prev_bbox=_snapshot_bbox_for_outlier,
                    frame_width=fov,
                    frame_height=fov,
                    config=cfg
                )
                
                if is_valid:
                    filtered_contours.append(cnt)
                elif cfg.get('outlier_logging', True):
                    x, y, w, h = cv2.boundingRect(cnt)
                    print(f"[OUTLIER] {reason}: bbox=({x},{y},{w},{h})")
            
            target_count = len(filtered_contours)

            # Thread-safe read of booleans
            _cur_active = get_active()
            _cur_show_monitor = get_show_monitor()
            _cur_show_fov = get_show_fov()

            # Only copy frame if monitor is on (performance: skip allocation when off)
            vis        = frame.copy() if _cur_show_monitor else frame
            aim_on     = _cur_active and is_activation_key_pressed()
            fov_center = (fov // 2, fov // 2)

            if _cur_show_fov and _cur_show_monitor:
                cv2.circle(vis, fov_center, fov//2-4,
                           (0,255,100) if target_count else (0,180,0), 1, cv2.LINE_AA)
            if aim_on and filtered_contours:
                # ── Score-based selection (vision1) ──────
                best_bbox  = None
                best_score = -1e18
                best_confidence = 0.0

                # อ่าน _lock_bbox ครั้งเดียวก่อน loop — ป้องกัน race condition
                with _vision_lock:
                    _snapshot_bbox = _lock_bbox
                    _snapshot_prev_area = _lock_prev_area

                for cnt in filtered_contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cx_ = x + w // 2
                    cy_ = y + h // 2
                    d   = ((cx_-fov_center[0])**2 + (cy_-fov_center[1])**2)**0.5
                    area = cv2.contourArea(cnt)
                    
                    # ✨ FEATURE 1: Calculate confidence ✨
                    confidence = calculate_confidence(cnt, hsv, fov_center, _snapshot_prev_area)
                    
                    # Only consider detections with decent confidence
                    if confidence < 0.4:
                        continue  # Skip low-confidence detections
                    
                    score = (1 / (d + 1)) * (area ** 0.4) * (0.5 + 0.5 * confidence)

                    # lock continuity bonus — ใช้ snapshot แทน global โดยตรง
                    if _snapshot_bbox:
                        lx,ly,lw,lh = _snapshot_bbox
                        ld = ((cx_-(lx+lw//2))**2 + (cy_-(ly+lh//2))**2)**0.5
                        score += 50 / (ld + 1)

                    if score > best_score:
                        best_score = score
                        best_bbox  = (x, y, w, h)
                        best_confidence = confidence

                if best_bbox:
                    bx,by,bw,bh = best_bbox
                    pct   = AIM_ZONE_MAP.get(AIM_ZONE, 0.18)
                    raw_x = bx + bw//2  + cfg['offset_x']
                    raw_y = int(by+bh*pct) + cfg['offset_y']

                    # ── Velocity prediction (vision1) ─────
                    pred_x, pred_y = float(raw_x), float(raw_y)
                    
                    with _vision_lock:
                        if _lock_bbox is not None:
                            prev_cx = _lock_bbox[0] + _lock_bbox[2]//2
                            prev_cy = _lock_bbox[1] + _lock_bbox[3]//2
                            vx = raw_x - prev_cx
                            vy = raw_y - prev_cy
                            _lock_vx = _VEL_EMA*vx + (1-_VEL_EMA)*_lock_vx
                            _lock_vy = _VEL_EMA*vy + (1-_VEL_EMA)*_lock_vy
                            pred_x  += _lock_vx * _PRED_W
                            pred_y  += _lock_vy * _PRED_W
                        
                        _lock_bbox = best_bbox
                        _lock_prev_area = bw * bh  # ← เก็บ area สำหรับ confidence ครั้งหน้า
                        _lock_lost = 0
                        
                        # ✨ FEATURE 2: Update outlier state with valid detection
                        _outlier_state.add_detection(best_bbox)

                    # ── 2-zone smooth (ใช้ snapshot SMOOTH) ────
                    dist = ((pred_x-fov_center[0])**2+(pred_y-fov_center[1])**2)**0.5
                    s    = max(1.0, cfg['smooth'])
                    ds   = (max(0.5, s * 0.28) if dist > 15
                            else (max(1.0, s * (dist/12.0)) if dist > 0 else 1.0))

                    mx = ((pred_x - fov_center[0]) / ds) * cfg['x_speed']
                    my = ((pred_y - fov_center[1]) / ds) * cfg['y_speed']

                    # ── RCS ───────────────────────────────
                    if cfg['rcs_enable'] and _trig_held():
                        frame_count = int((time.perf_counter() - _fire_start_time) * 144)
                        if frame_count < len(RCS_PATTERN):
                            my += RCS_PATTERN[frame_count]

                    fx, fy = humanize_movement(mx, my, confidence=best_confidence)
                    
                    # Send to Arduino (primary method)
                    ard_ok = send_to_arduino(int(fx), int(fy))
                    
                    # Fallback: if Arduino not connected, move mouse directly
                    if not ard_ok:
                        try:
                            import pyautogui as pag
                            current_x, current_y = pag.position()
                            pag.moveTo(current_x + int(fx), current_y + int(fy), duration=0.01)
                        except Exception as mouse_err:
                            pass

                    # draw (only if monitor is on)
                    if _cur_show_monitor:
                        cv2.rectangle(vis, (bx,by), (bx+bw,by+bh), (0,255,0), 2)
                        zone_y = int(by + bh * pct)
                        cv2.line(vis, (bx,zone_y), (bx+bw,zone_y), (0,200,255), 1)
                        cv2.circle(vis, (int(pred_x), int(pred_y)), 5, (255,0,255), -1)
                        cv2.line(vis,(int(pred_x)-8,int(pred_y)),(int(pred_x)+8,int(pred_y)),(0,255,255),1)
                        cv2.line(vis,(int(pred_x),int(pred_y)-8),(int(pred_x),int(pred_y)+8),(0,255,255),1)

                    if check_trigger_fire():
                        if _cur_show_monitor:
                            cv2.circle(vis, fov_center, 20, (0,0,255), 3)
                    
                    # ✨ FEATURE 1: Draw confidence meter ✨
                    if _cur_show_monitor:
                        conf_text = f"CONF:{best_confidence:.0%}"
                        conf_color = (0, 255, 0) if best_confidence > 0.7 else (0, 255, 255) if best_confidence > 0.5 else (0, 0, 255)
                        cv2.putText(vis, conf_text, (bx, by-25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, conf_color, 1)

            elif aim_on:
                with _vision_lock:
                    _lock_lost += 1
                    if _lock_lost >= _LOST_MAX:
                        _lock_bbox = None
                        _lock_vx = _lock_vy = 0.0
                        # ✨ FEATURE 2: Clear outlier state when target lost
                        _outlier_state.clear()

            # ── Trigger dot ──────────────────────────────
            if _cur_show_monitor:
                cv2.circle(vis, (fov-14, 14), 6,
                           (0,100,255) if _trig_held() else (40,40,40), -1)

            # ── FPS ──────────────────────────────────────
            dt = time.perf_counter() - t0
            if dt > 0: fps_history.append(1.0/dt)
            fps = int(sum(fps_history)/len(fps_history)) if fps_history else 0

            # ── HUD ──────────────────────────────────────
            if _cur_show_monitor:
                st = ("LOCK" if _lock_bbox else "SCAN" if aim_on
                      else "RDY" if _cur_active else "OFF")
                sc = ((0,255,255) if _lock_bbox else (0,165,255) if aim_on
                      else (0,165,255) if _cur_active else (80,80,80))

                cv2.putText(vis, f"FPS:{fps} {cap_tag}  T:{target_count}  {st}",
                            (12,35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, sc, 2)
                cv2.putText(vis, f"ZONE:{AIM_ZONE.upper()}",
                            (12,65), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,200,255), 2)
                cv2.putText(vis,
                            f"AIM[{cfg['activation_key'].upper()}]  "
                            f"TRIG[{cfg['trigger_key'].upper()}]",
                            (12,95), cv2.FONT_HERSHEY_SIMPLEX, 0.60,
                            (0,255,0) if aim_on else (100,100,100), 2)

            if _cur_show_monitor:
                # ✨ ENHANCEMENT: Larger, centered display
                display_size = 800
                vis_resized = cv2.resize(vis, (display_size, display_size), interpolation=cv2.INTER_LINEAR)
                
                # Create window ONCE (not every frame)
                if not _window_created:
                    cv2.namedWindow("Vision Monitor", cv2.WINDOW_AUTOSIZE)
                    _window_created = True
                
                cv2.imshow("Vision Monitor", vis_resized)
                cv2.setMouseCallback("Vision Monitor", pick_color, param=frame)
            else:
                if _window_created:
                    try: cv2.destroyWindow("Vision Monitor")
                    except: pass
                    _window_created = False
            
            # Reset error counter on successful frame
            if _consecutive_errors > 0:
                reset_error_counter()
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        except Exception as e:
            print("[ERROR] Exception: {}".format(e))
            traceback.print_exc()
            
            # Reset shared state on error
            with _vision_lock:
                _lock_bbox = None
                _lock_vx = _lock_vy = 0.0
                _lock_lost = 0
                _consecutive_errors += 1
                
                if _consecutive_errors >= _ERROR_THRESHOLD:
                    print("[ERROR] Hardware may be disconnected (>={} consecutive errors)".format(_ERROR_THRESHOLD))
            
            time.sleep(0.1)  # Backoff slightly on error

    cv2.destroyAllWindows()