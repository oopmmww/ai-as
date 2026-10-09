import json, os, threading, copy
import numpy as np

try:
    import pyautogui as _pg
    _W, _H = _pg.size()
except Exception:
    _W, _H = 1920, 1080

class Config:
    def __init__(self):
        self._lock         = threading.RLock()  # RLock: reentrant — ป้องกัน deadlock ใน switch_profile→load
        self.CONFIG_FILE   = "aimbot_config.json"
        # ── Hardware ──────────────────────────────────────
        self.SERIAL_PORT   = "COM3"
        self.SERIAL_BAUD   = 115200
        self.SCREEN_WIDTH  = _W
        self.SCREEN_HEIGHT = _H
        print(f"[SCREEN] {_W}x{_H}")

        # ── Detection ─────────────────────────────────────
        self.FOV           = 170     # capture zone size (px)
        self.MIN_AREA      = 5
        self.MAX_AREA      = 20000
        self.USE_SIMILARITY = False  # True = similarity map, False = inRange

        # ── Aim ───────────────────────────────────────────
        self.X_SPEED       = 0.35  # speed multiplier X  (0.1 ~ 2.0)
        self.Y_SPEED       = 0.38  # speed multiplier Y
        self.SMOOTH        = 8.0    # aim smoothing divisor (1=เร็ว 8=ช้า)
        self.OFFSET_X      = 0
        self.OFFSET_Y      = 0

        # ── Keys ──────────────────────────────────────────
        self.ACTIVATION_KEY = "alt"   # ปุ่ม hold เพื่อ aim
        self.TRIGGER_KEY    = "mouse1" # ปุ่มกดเองเพื่อยิง
        self.TRIGGER_DELAY  = 50       # ms cooldown

        # ── RCS ───────────────────────────────────────────
        self.RCS_ENABLE    = False
        self.RCS_STRENGTH  = 3.5     # Y offset ขณะยิง (ชดเชย recoil)

        # ── Triggerbot Zone ───────────────────────────────
        self.TRG_ZONE_ON   = False
        self.TRG_ZONE_SIZE = 6       # ±px ที่ crosshair
        self.TRG_ZONE_PX   = 3       # จำนวน pixel ขั้นต่ำ

        # ── Humanize ──────────────────────────────────────
        self.HUMANIZE      = True
        self.HUMAN_STR     = 0.5    # noise strength

        # ── Color ─────────────────────────────────────────
        self._lower_color  = np.array([130, 60,  70])
        self._upper_color  = np.array([175, 255, 255])

        # ── Profile ───────────────────────────────────────
        self.ACTIVE_PROFILE = "default"
        
        # ── Logging (Phase 5) ──────────────────────────────
        self.LOGGING_ENABLED = True  # Toggle เก็บ logs หรือไม่

    # ─── Thread-safe Color Properties ────────────────────────
    # np.ndarray is mutable → must do atomic reference swap
    @property
    def LOWER_COLOR(self):
        with self._lock:
            return self._lower_color.copy()

    @LOWER_COLOR.setter
    def LOWER_COLOR(self, value):
        arr = np.array(value) if not isinstance(value, np.ndarray) else value.copy()
        with self._lock:
            self._lower_color = arr

    @property
    def UPPER_COLOR(self):
        with self._lock:
            return self._upper_color.copy()

    @UPPER_COLOR.setter
    def UPPER_COLOR(self, value):
        arr = np.array(value) if not isinstance(value, np.ndarray) else value.copy()
        with self._lock:
            self._upper_color = arr

    # ─── Atomic Snapshot for Vision Loop ─────────────────────
    def get_detection_params(self):
        """Return atomic snapshot of detection-related config.
        Vision loop should call this ONCE per frame instead of
        accessing individual attributes multiple times."""
        with self._lock:
            return {
                'fov': self.FOV,
                'lower_color': self._lower_color.copy(),
                'upper_color': self._upper_color.copy(),
                'min_area': self.MIN_AREA,
                'max_area': self.MAX_AREA,
                'x_speed': self.X_SPEED,
                'y_speed': self.Y_SPEED,
                'smooth': self.SMOOTH,
                'offset_x': self.OFFSET_X,
                'offset_y': self.OFFSET_Y,
                'rcs_enable': self.RCS_ENABLE,
                'rcs_strength': self.RCS_STRENGTH,
                'humanize': self.HUMANIZE,
                'human_str': self.HUMAN_STR,
                'activation_key': self.ACTIVATION_KEY,
                'trigger_key': self.TRIGGER_KEY,
                'trigger_delay': self.TRIGGER_DELAY,
            }

    # ─── Save ───────────────────────────────────────────────
    def save(self, profile: str = None):
        with self._lock:
            profile = profile or self.ACTIVE_PROFILE
            data = {}
            for k, v in vars(self).items():
                if k.startswith("_") or k == "CONFIG_FILE": continue
                data[k] = v.tolist() if isinstance(v, np.ndarray) else v
            # Include color properties (stored as _lower/_upper)
            data['LOWER_COLOR'] = self._lower_color.tolist()
            data['UPPER_COLOR'] = self._upper_color.tolist()
            try:
                all_p = {}
                if os.path.exists(self.CONFIG_FILE):
                    with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                        all_p = json.load(f)
                if not isinstance(all_p, dict): all_p = {}
                all_p[profile] = data
                with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_p, f, indent=4)
                print(f"💾 Saved [{profile}]")
            except Exception as e:
                print(f"⚠️ Save failed: {e}")

    # ─── Load ───────────────────────────────────────────────
    def load(self, profile: str = None):
        with self._lock:
            profile = profile or self.ACTIVE_PROFILE
            if not os.path.exists(self.CONFIG_FILE): return
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    all_p = json.load(f)
                if not isinstance(all_p, dict): return
                fv = next(iter(all_p.values()), None)
                data = all_p if not isinstance(fv, dict) else all_p.get(profile, {})
                for k, v in data.items():
                    if k in ("SCREEN_WIDTH", "SCREEN_HEIGHT"): continue
                    # Color properties use setter (which acquires lock — RLock is reentrant)
                    if k in ("LOWER_COLOR", "UPPER_COLOR") and isinstance(v, list):
                        setattr(self, k, np.array(v))
                    elif hasattr(self, k):
                        setattr(self, k, v)
                print(f"✅ Config [{profile}]")
            except Exception as e:
                print(f"⚠️ Load failed: {e}")

    def list_profiles(self) -> list:
        with self._lock:
            if not os.path.exists(self.CONFIG_FILE): return ["default"]
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                fv = next(iter(d.values()), None)
                return ["default"] if not isinstance(fv, dict) else list(d.keys())
            except: return ["default"]

    def switch_profile(self, name: str):
        with self._lock:
            self.ACTIVE_PROFILE = name
            self.load(name)

config = Config()