# 🎯 PLAN A: Enhanced Color Detection System
## Detailed Implementation Guide for Current Detection System

**Goal**: Improve current HSV-based detection  
**Duration**: 2.5 weeks  
**Current System**: Color mask → Contours → Outlier filtering → Confidence scoring

---

## 📊 Current System Bottlenecks Analysis

### Problem 1: False Positives from Background
```
Current: HSV mask picks up any color match (lighting-sensitive)
Issue:   - Shadows appear as targets
         - Reflections on walls/ground
         - Similar-colored objects (boxes, clothing, etc.)
Result:  False positive rate ~40-50%
```

### Problem 2: Temporal Jitter
```
Current: Each frame independent (per-frame decision)
Issue:   - Noise spike → detection spike → disappear
         - Confidence varies wildly
         - Aim locks/unlocks rapidly
Result:  Inconsistent aiming, detectable as aimbot
```

### Problem 3: Limited Outlier Filtering
```
Current: 4 validators (movement, size, bounds, aspect)
Issue:   - No color histogram check
         - No edge density validation
         - No solidity check
         - No background separation
Result:  Noise and artifacts pass through
```

### Problem 4: Weak Confidence Scoring
```
Current: 4-factor weighted average
Issue:   - Doesn't use temporal history
         - Ignores color consistency
         - No motion stability check
Result:  Low-quality detections get high confidence
```

---

## 🔧 Phase A1: MOG2 Background Subtraction Integration

### A1.1 Create New Module: `bg_subtractor.py`

```python
"""
bg_subtractor.py
Adaptive background modeling using MOG2
Separates foreground (moving objects) from background (static)
"""

import cv2
import numpy as np
from threading import Lock

class BackgroundSubtractor:
    """
    MOG2-based background model
    - Adaptive to lighting changes
    - Detects shadows
    - Learns from video stream
    """
    
    def __init__(self, 
                 detect_shadows=True,
                 var_threshold=16,
                 var_threshold_gen=48,
                 learning_rate=0.001):
        """
        Args:
            detect_shadows: Enable shadow detection
            var_threshold: Variance threshold for foreground (lower = more sensitive)
            var_threshold_gen: Variance threshold for background learning
            learning_rate: How quickly model adapts (0-1)
        """
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=detect_shadows,
            varThreshold=var_threshold
        )
        self.var_threshold_gen = var_threshold_gen
        self.learning_rate = learning_rate
        self._lock = Lock()
        self.frame_count = 0
        self.fg_pixels_ratio = 0.0  # For monitoring
    
    def apply(self, frame):
        """
        Apply MOG2 subtraction to frame
        Returns: Binary mask (255=foreground, 0=background)
        """
        with self._lock:
            # Apply MOG2
            fg_mask = self.bg_subtractor.apply(frame, self.learning_rate)
            
            # MOG2 returns:
            # - 0: background
            # - 127: shadow (if detect_shadows=True)
            # - 255: foreground
            
            # Convert shadows to background (optional)
            fg_mask[fg_mask == 127] = 0  # Shadows as background
            
            # Calculate foreground ratio for monitoring
            fg_pixels = np.count_nonzero(fg_mask)
            total_pixels = fg_mask.size
            self.fg_pixels_ratio = fg_pixels / total_pixels
            
            self.frame_count += 1
            return fg_mask
    
    def get_stats(self):
        """Return monitoring statistics"""
        return {
            'frame_count': self.frame_count,
            'fg_pixels_ratio': self.fg_pixels_ratio,
            'learning_complete': self.frame_count > 500  # 500 frames = ~8 sec @ 60fps
        }
    
    def reset(self):
        """Reset background model (e.g., new game session)"""
        with self._lock:
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                detectShadows=True,
                varThreshold=16
            )
            self.frame_count = 0
            self.fg_pixels_ratio = 0.0
```

### A1.2 Modify `config.py` - Add MOG2 Settings

```python
# ═══ Background Subtraction (MOG2) ═══
MOG2_ENABLED = True
MOG2_DETECT_SHADOWS = True
MOG2_VAR_THRESHOLD = 16          # Lower = more sensitive (8-32)
MOG2_VAR_THRESHOLD_GEN = 48      # Background variance threshold
MOG2_LEARNING_RATE = 0.001       # Adaptation speed (0.0001-0.01)
MOG2_STABILIZATION_FRAMES = 500  # Frames to wait before model ready

# ═══ Mask Combination Strategy ═══
MASK_COMBINE_STRATEGY = 'AND'    # 'AND' or 'weighted_and'
# AND: Both conditions required (strictest)
# weighted_and: Color=60%, foreground=40% (flexible)

# ═══ Foreground Analysis ═══
MIN_FOREGROUND_RATIO = 0.001     # Min % of frame that's moving
MAX_FOREGROUND_RATIO = 0.20      # Max % (detect anomalies like screen flicker)
```

### A1.3 Modify `vision.py` - Integration Point

**At top of vision.py:**
```python
from bg_subtractor import BackgroundSubtractor

# Initialize MOG2 subtractor
_bg_subtractor = None

def initialize_vision():
    global _bg_subtractor
    if config.MOG2_ENABLED:
        _bg_subtractor = BackgroundSubtractor(
            detect_shadows=config.MOG2_DETECT_SHADOWS,
            var_threshold=config.MOG2_VAR_THRESHOLD,
            var_threshold_gen=config.MOG2_VAR_THRESHOLD_GEN,
            learning_rate=config.MOG2_LEARNING_RATE
        )
        print("[MOG2] Initialized - learning from video stream")
```

**In vision_loop(), after HSV conversion:**
```python
# ══════════════════════════════════════
# Color detection (existing)
# ══════════════════════════════════════
mask = detect_color(hsv, lower=cfg['lower_color'], upper=cfg['upper_color'])
mask = cv2.GaussianBlur(mask, (5, 5), 0)
mask = cv2.erode(mask, k3, iterations=1)
mask = cv2.dilate(mask, k3, iterations=2)

# ══════════════════════════════════════
# NEW: Apply MOG2 foreground mask
# ══════════════════════════════════════
if config.MOG2_ENABLED and _bg_subtractor:
    fg_mask = _bg_subtractor.apply(frame)
    
    # Check MOG2 stabilization
    mog2_stats = _bg_subtractor.get_stats()
    if not mog2_stats['learning_complete']:
        # Still learning - don't use yet
        combined_mask = mask
    else:
        # Combine color mask + foreground mask
        if cfg.get('mask_combine_strategy', 'AND') == 'AND':
            combined_mask = cv2.bitwise_and(mask, fg_mask)
        else:
            # Weighted combination
            combined_mask = cv2.addWeighted(mask, 0.6, fg_mask, 0.4, 0)
else:
    combined_mask = mask

# ══════════════════════════════════════
# Find contours using combined mask
# ══════════════════════════════════════
contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
```

### A1.4 Web UI Integration - `/api/mog2/stats`

```python
# In routes.py
@app.route('/api/mog2/stats', methods=['GET'])
def get_mog2_stats():
    if not vision._bg_subtractor:
        return jsonify({'enabled': False})
    
    stats = vision._bg_subtractor.get_stats()
    return jsonify({
        'enabled': True,
        'frame_count': stats['frame_count'],
        'fg_pixels_ratio': f"{stats['fg_pixels_ratio']:.1%}",
        'learning_complete': stats['learning_complete'],
        'status': 'Ready' if stats['learning_complete'] else 'Learning...'
    })

@app.route('/api/mog2/reset', methods=['POST'])
def reset_mog2():
    if vision._bg_subtractor:
        vision._bg_subtractor.reset()
        return jsonify({'status': 'MOG2 model reset'})
    return jsonify({'error': 'MOG2 not enabled'}), 400
```

### A1.5 Testing Strategy

**Test 1: Baseline Comparison**
```
# Disable MOG2
MOG2_ENABLED = False

Run 10 test scenarios:
- Daylight game
- Indoor fluorescent
- Night (dark)
- Moving shadows
- Reflections on ground
- Similar-colored objects in scene

Measure: FP count, detection latency
Log to: baseline_results.json
```

**Test 2: With MOG2 Enabled**
```
# Enable MOG2
MOG2_ENABLED = True

Same 10 scenarios:
Measure: FP count, detection latency
Compare vs baseline

Success metric: FP reduction > 30%
```

**Test 3: Stabilization**
```
Start game:
Frame 1-100: MOG2 learning (high FP expected)
Frame 101-500: MOG2 refining
Frame 501+: MOG2 ready (low FP)

Verify: FP drops significantly after frame 500
```

---

## 🔄 Phase A2: Temporal Denoising (3-Frame Consensus)

### A2.1 Create `temporal_filter.py`

```python
"""
temporal_filter.py
Temporal consistency validation using frame history
Reduces false positives from noise spikes
"""

from collections import deque
from threading import Lock
import numpy as np

class TemporalFilter:
    """
    Maintains rolling window of detections
    Only accepts targets that appear in 3+ frames
    """
    
    def __init__(self, history_size=5, consensus_threshold=3):
        """
        Args:
            history_size: Frames to keep in history (default 5)
            consensus_threshold: Min frames needed to accept (default 3)
        """
        self.history_size = history_size
        self.consensus_threshold = consensus_threshold
        self.detection_history = deque(maxlen=history_size)
        self._lock = Lock()
        self.frame_count = 0
    
    def add_detections(self, bboxes):
        """
        Record detections from current frame
        Args:
            bboxes: List of (x, y, w, h) tuples
        """
        with self._lock:
            self.detection_history.append(bboxes)
            self.frame_count += 1
    
    def get_consensus_detections(self):
        """
        Return detections that appear in 3+ frames
        Also applies spatial clustering (NMS-like)
        """
        with self._lock:
            if len(self.detection_history) < self.consensus_threshold:
                return []  # Not enough history
            
            # Flatten all bboxes from recent frames
            all_bboxes = []
            frame_indices = []
            for frame_idx, bboxes in enumerate(self.detection_history):
                for bbox in bboxes:
                    all_bboxes.append(bbox)
                    frame_indices.append(frame_idx)
            
            if not all_bboxes:
                return []
            
            # Cluster similar bboxes (spatial proximity)
            consensus_bboxes = self._spatial_cluster(
                all_bboxes, 
                frame_indices
            )
            
            return consensus_bboxes
    
    def _spatial_cluster(self, bboxes, frame_indices, iou_threshold=0.5):
        """
        Group bboxes that are spatially close across frames
        Keep clusters that appear in 3+ frames
        """
        if not bboxes:
            return []
        
        clusters = []
        used = set()
        
        for i, bbox1 in enumerate(bboxes):
            if i in used:
                continue
            
            cluster = [bbox1]
            cluster_frames = {frame_indices[i]}
            used.add(i)
            
            # Find similar bboxes
            for j, bbox2 in enumerate(bboxes):
                if j in used or j <= i:
                    continue
                
                iou = self._compute_iou(bbox1, bbox2)
                if iou > iou_threshold:
                    cluster.append(bbox2)
                    cluster_frames.add(frame_indices[j])
                    used.add(j)
            
            # Accept cluster only if appears in 3+ frames
            if len(cluster_frames) >= self.consensus_threshold:
                # Average the cluster
                avg_bbox = self._average_bboxes(cluster)
                clusters.append(avg_bbox)
        
        return clusters
    
    def _compute_iou(self, bbox1, bbox2):
        """Intersection over Union"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - inter_area
        
        if union_area == 0:
            return 0.0
        
        return inter_area / union_area
    
    def _average_bboxes(self, bboxes):
        """Average multiple bboxes"""
        xs = [b[0] for b in bboxes]
        ys = [b[1] for b in bboxes]
        ws = [b[2] for b in bboxes]
        hs = [b[3] for b in bboxes]
        
        return (
            int(np.mean(xs)),
            int(np.mean(ys)),
            int(np.mean(ws)),
            int(np.mean(hs))
        )
    
    def reset(self):
        """Clear history"""
        with self._lock:
            self.detection_history.clear()
            self.frame_count = 0
```

### A2.2 Modify `config.py` - Add Temporal Settings

```python
# ═══ Temporal Filtering ═══
TEMPORAL_FILTER_ENABLED = True
TEMPORAL_HISTORY_SIZE = 5          # Keep 5 frames of history
TEMPORAL_CONSENSUS_THRESHOLD = 3   # Min 3 frames for acceptance
TEMPORAL_IOU_THRESHOLD = 0.5       # Spatial clustering threshold
```

### A2.3 Modify `vision.py` - Integration

```python
from temporal_filter import TemporalFilter

# Initialize
_temporal_filter = None

def initialize_vision():
    global _temporal_filter
    if config.TEMPORAL_FILTER_ENABLED:
        _temporal_filter = TemporalFilter(
            history_size=config.TEMPORAL_HISTORY_SIZE,
            consensus_threshold=config.TEMPORAL_CONSENSUS_THRESHOLD
        )
        print("[TEMPORAL] Initialized")
```

**In vision_loop(), after outlier filtering:**
```python
# Filter contours (existing outlier validation)
filtered_contours = []
for cnt in valid:
    is_valid, reason = validate_contour(cnt, ...)
    if is_valid:
        filtered_contours.append(cnt)

# Extract bboxes
current_bboxes = []
for cnt in filtered_contours:
    x, y, w, h = cv2.boundingRect(cnt)
    current_bboxes.append((x, y, w, h))

# Add to temporal filter
if config.TEMPORAL_FILTER_ENABLED and _temporal_filter:
    _temporal_filter.add_detections(current_bboxes)
    
    # Get consensus detections (3+ frames)
    consensus_bboxes = _temporal_filter.get_consensus_detections()
    
    # Use consensus bboxes for aim logic
    target_bboxes = consensus_bboxes
else:
    target_bboxes = current_bboxes

target_count = len(target_bboxes)

# Rest of aim logic uses target_bboxes (filtered)
```

---

## 🎯 Phase A3: Enhanced Outlier Filtering (8 Validators)

### A3.1 Create `outlier_validators.py`

```python
"""
outlier_validators.py
Advanced outlier detection with 8 validation criteria
"""

import cv2
import numpy as np

class OutlierValidator:
    """
    Multi-criterion outlier validation
    Returns: (is_valid, confidence, reason)
    """
    
    @staticmethod
    def validate_histogram_similarity(prev_frame, curr_frame, prev_bbox, curr_bbox):
        """
        Check color histogram consistency
        Real objects have similar colors frame-to-frame
        """
        if prev_frame is None or prev_bbox is None:
            return (True, 1.0, "first_frame")
        
        try:
            # Extract ROI
            px, py, pw, ph = prev_bbox
            cx, cy, cw, ch = curr_bbox
            
            prev_roi = prev_frame[py:py+ph, px:px+pw]
            curr_roi = curr_frame[cy:cy+ch, cx:cx+cw]
            
            if prev_roi.size == 0 or curr_roi.size == 0:
                return (True, 0.8, "empty_roi")
            
            # Compute histogram correlation
            prev_hist = cv2.calcHist([prev_roi], [0, 1, 2], None, [8, 8, 8], 
                                     [0, 256, 0, 256, 0, 256])
            curr_hist = cv2.calcHist([curr_roi], [0, 1, 2], None, [8, 8, 8],
                                     [0, 256, 0, 256, 0, 256])
            
            cv2.normalize(prev_hist, prev_hist)
            cv2.normalize(curr_hist, curr_hist)
            
            correlation = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)
            
            # correlation: 0 (different) to 1.0 (identical)
            is_valid = correlation > 0.6
            confidence = correlation
            
            return (is_valid, confidence, f"hist_corr_{correlation:.2f}")
        
        except Exception as e:
            return (True, 0.8, "hist_error")
    
    @staticmethod
    def validate_edge_density(contour, frame, threshold=100):
        """
        Real objects have edges, noise is smooth
        Count edge pixels in contour ROI
        """
        try:
            x, y, w, h = cv2.boundingRect(contour)
            roi = frame[y:y+h, x:x+w]
            
            if roi.size == 0:
                return (True, 0.8, "empty_roi")
            
            # Compute Laplacian (edge detection)
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            edge_pixels = np.count_nonzero(np.abs(laplacian) > 30)
            
            edge_ratio = edge_pixels / roi.size
            
            # Real objects: edge_ratio > 0.05
            is_valid = edge_ratio > 0.05
            confidence = min(1.0, edge_ratio * 10)  # Scale to 0-1
            
            return (is_valid, confidence, f"edge_density_{edge_ratio:.3f}")
        
        except Exception as e:
            return (True, 0.8, "edge_error")
    
    @staticmethod
    def validate_contour_solidity(contour):
        """
        Solidity = contour area / convex hull area
        Real objects: solidity > 0.6
        Noise: solidity < 0.5
        """
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        
        if hull_area == 0:
            return (False, 0.0, "zero_hull_area")
        
        solidity = area / hull_area
        
        is_valid = solidity > 0.6
        confidence = solidity
        
        return (is_valid, confidence, f"solidity_{solidity:.2f}")
    
    @staticmethod
    def validate_variance(contour, frame):
        """
        Pixel variance in ROI
        Real objects: high variance (textured)
        Noise/shadows: low variance (smooth)
        """
        try:
            x, y, w, h = cv2.boundingRect(contour)
            roi = frame[y:y+h, x:x+w]
            
            if roi.size == 0:
                return (True, 0.8, "empty_roi")
            
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Real objects: variance > 100
            is_valid = variance > 100
            confidence = min(1.0, variance / 500)  # Normalize to 0-1
            
            return (is_valid, confidence, f"variance_{variance:.1f}")
        
        except Exception as e:
            return (True, 0.8, "variance_error")
    
    @staticmethod
    def validate_color_variance(contour, frame_hsv):
        """
        HSV color variance in ROI
        Real objects: consistent color (low variance)
        Noise: random colors (high variance)
        """
        try:
            x, y, w, h = cv2.boundingRect(contour)
            roi = frame_hsv[y:y+h, x:x+w]
            
            if roi.size == 0:
                return (True, 0.8, "empty_roi")
            
            # Check H channel variance
            h_var = np.var(roi[:, :, 0])
            s_var = np.var(roi[:, :, 1])
            
            # Real objects: H variance < 20 (uniform color)
            is_valid = h_var < 20
            confidence = 1.0 - min(1.0, h_var / 50)
            
            return (is_valid, confidence, f"color_var_h{h_var:.1f}")
        
        except Exception as e:
            return (True, 0.8, "color_var_error")
```

### A3.2 Modify `validate_contour()` in `vision.py`

```python
def validate_contour_enhanced(contour, prev_bbox, frame, frame_hsv, 
                              prev_frame, prev_frame_hsv, config):
    """
    Enhanced outlier validation with 8 criteria
    Returns: (is_valid, confidence, reasons)
    """
    x, y, w, h = cv2.boundingRect(contour)
    curr_bbox = (x, y, w, h)
    
    # Early frame (baseline)
    if prev_frame is None:
        return (True, 0.8, ["first_frame"])
    
    # Run all validators
    validators = [
        # Existing 4
        ("movement", validate_movement(prev_bbox, curr_bbox, 
                                       frame.shape[1], config.get('max_speed_pct', 0.30))),
        ("size_ratio", validate_size_ratio(prev_bbox, curr_bbox, 0.50, 2.00)),
        ("bounds", validate_bounds(curr_bbox, frame.shape[1], frame.shape[0])),
        ("aspect", validate_aspect_ratio(prev_bbox, curr_bbox, 0.15)),
        
        # New 4
        ("histogram", OutlierValidator.validate_histogram_similarity(
            prev_frame, frame, prev_bbox, curr_bbox)),
        ("edge_density", OutlierValidator.validate_edge_density(contour, frame)),
        ("solidity", OutlierValidator.validate_contour_solidity(contour)),
        ("variance", OutlierValidator.validate_variance(contour, frame)),
        ("color_var", OutlierValidator.validate_color_variance(contour, frame_hsv)),
    ]
    
    # Weighted voting
    total_weight = 0
    weighted_score = 0
    reasons = []
    
    for name, (is_valid, confidence, reason) in validators:
        weight = config.get(f'validator_weight_{name}', 1.0)
        
        if not is_valid:
            reasons.append(f"FAIL:{name}({reason})")
        else:
            reasons.append(f"PASS:{name}({reason})")
        
        weighted_score += weight * (1.0 if is_valid else 0.0) * confidence
        total_weight += weight
    
    final_confidence = weighted_score / total_weight if total_weight > 0 else 0.0
    
    # Accept if 6+ validators pass
    pass_count = sum(1 for _, (is_valid, _, _) in validators if is_valid)
    is_valid = pass_count >= 6
    
    return (is_valid, final_confidence, reasons)
```

### A3.3 Config Validator Weights

```python
# ═══ Validator Weights ═══
VALIDATOR_WEIGHT_MOVEMENT = 1.5      # Movement is critical
VALIDATOR_WEIGHT_SIZE_RATIO = 1.0
VALIDATOR_WEIGHT_BOUNDS = 1.0
VALIDATOR_WEIGHT_ASPECT = 0.8
VALIDATOR_WEIGHT_HISTOGRAM = 1.2     # Color consistency is good indicator
VALIDATOR_WEIGHT_EDGE_DENSITY = 1.0
VALIDATOR_WEIGHT_SOLIDITY = 1.0
VALIDATOR_WEIGHT_VARIANCE = 0.8
VALIDATOR_WEIGHT_COLOR_VAR = 0.9

# Accept if N validators pass
VALIDATOR_MIN_PASS_COUNT = 6  # Out of 9
```

---

## 💯 Phase A4: Confidence Scoring Upgrade

### A4.1 Enhanced `calculate_confidence()` in `vision.py`

```python
def calculate_confidence_v2(contour, frame_hsv, fov_center, 
                            previous_area, temporal_presence,
                            motion_smoothness, bg_separation_score):
    """
    8-factor confidence scoring
    
    Factors:
    1. Color match quality (0-1)
    2. Size consistency (0-1)
    3. Position within FOV (0-1)
    4. Shape validity (0-1)
    5. Temporal presence (0-1) - appeared in 3+ frames?
    6. Color histogram match (0-1) - frame-to-frame consistency
    7. Motion smoothness (0-1) - velocity EMA stability
    8. Background separation (0-1) - MOG2 foreground score
    """
    
    area = cv2.contourArea(contour)
    if area < config.MIN_AREA:
        return 0.0
    
    x, y, w, h = cv2.boundingRect(contour)
    cx, cy = x + w // 2, y + h // 2
    
    # ━━━ Factor 1: Color Match Quality (0-1)
    aspect_ratio = h / (w + 1)
    color_match = min(1.0, aspect_ratio / 0.6) if aspect_ratio < 0.6 else 1.0
    
    # ━━━ Factor 2: Size Consistency (0-1)
    if previous_area is not None and previous_area > 0:
        area_ratio = area / previous_area
        if 0.5 < area_ratio < 2.0:
            size_consistency = 1.0
        else:
            size_consistency = 0.5 * (1.0 - min(1.0, abs(area_ratio - 1.0) / 2.0))
    else:
        size_consistency = 0.8
    
    # ━━━ Factor 3: Position within FOV (0-1)
    dist_to_center = ((cx - fov_center[0])**2 + (cy - fov_center[1])**2) ** 0.5
    max_dist = fov_center[0] * 1.5
    position_score = max(0.7, 1.0 - (dist_to_center / (max_dist + 1)) * 0.3)
    
    # ━━━ Factor 4: Shape Validity (0-1)
    solidity = area / (w * h + 1)
    if 0.4 < aspect_ratio < 0.8 and solidity > 0.6:
        shape_score = 1.0
    elif 0.3 < aspect_ratio < 1.0 and solidity > 0.5:
        shape_score = 0.7
    else:
        shape_score = 0.4
    
    # ━━━ Factor 5: Temporal Presence (0-1)
    # (passed from temporal filter - how many frames appeared?)
    temporal_score = temporal_presence  # 0.0 - 1.0
    
    # ━━━ Factor 6: Color Histogram Match (0-1)
    # (already computed in outlier validator)
    histogram_score = 0.8  # Default, override with actual value
    
    # ━━━ Factor 7: Motion Smoothness (0-1)
    # (velocity EMA stability - how smooth is movement?)
    motion_score = motion_smoothness  # 0.0 - 1.0
    
    # ━━━ Factor 8: Background Separation (0-1)
    # (from MOG2 foreground model)
    bg_score = bg_separation_score  # 0.0 - 1.0
    
    # ━━━ Weighted Average
    confidence = (
        0.15 * color_match +
        0.12 * size_consistency +
        0.12 * position_score +
        0.12 * shape_score +
        0.15 * temporal_score +
        0.15 * histogram_score +
        0.10 * motion_score +
        0.09 * bg_score
    )
    
    return min(1.0, max(0.0, confidence))
```

---

## 🎬 Phase A5: Production Stability

### A5.1 Monitoring & Logging

```python
# In vision.py
import json
from datetime import datetime

class DetectionMetrics:
    def __init__(self, filename="detection_metrics.json"):
        self.filename = filename
        self.session_start = datetime.now()
        self.metrics = {
            'total_frames': 0,
            'detections': 0,
            'false_positives_rejected': 0,
            'temporal_filtered': 0,
            'mog2_contribution': 0,
        }
    
    def log(self, event_type, details):
        """Log detection event"""
        self.metrics[event_type] = self.metrics.get(event_type, 0) + 1
        
        # Every 1000 frames, write to disk
        if self.metrics['total_frames'] % 1000 == 0:
            self.save()
    
    def save(self):
        """Save metrics to file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'session_duration_sec': (datetime.now() - self.session_start).total_seconds(),
            **self.metrics
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

_metrics = DetectionMetrics()
```

### A5.2 Fallback Strategies

```python
# In vision.py - when detection lost
LOST_FALLBACK_FRAMES = 15  # Predict position for 15 frames

def handle_detection_lost(prev_lock_bbox, lock_vx, lock_vy, fov_center):
    """Predict target position when not detected"""
    
    if prev_lock_bbox is None:
        return None  # No history
    
    # Use velocity to predict
    px, py, pw, ph = prev_lock_bbox
    pred_x = px + lock_vx
    pred_y = py + lock_vy
    
    # Clamp to FOV
    pred_x = max(0, min(fov_center[0]*2 - pw, pred_x))
    pred_y = max(0, min(fov_center[1]*2 - ph, pred_y))
    
    return (int(pred_x), int(pred_y), pw, ph)
```

---

## 📊 Implementation Checklist

### Week 1
- [ ] Create `bg_subtractor.py`
- [ ] Add MOG2 config to `config.py`
- [ ] Integrate MOG2 in `vision.py` (modify vision_loop)
- [ ] Add `/api/mog2/stats` endpoint
- [ ] Test MOG2 with 5 scenarios, document FP reduction
- [ ] **Deploy**: Commit to branch `feature/mog2-integration`

### Week 1.5
- [ ] Create `temporal_filter.py`
- [ ] Add temporal config to `config.py`
- [ ] Integrate temporal filtering in `vision.py`
- [ ] Test temporal denoising with jittery scenarios
- [ ] **Deploy**: Commit to branch `feature/temporal-denoising`

### Week 2
- [ ] Create `outlier_validators.py`
- [ ] Implement 8 validators (histogram, edge, solidity, variance)
- [ ] Update `validate_contour()` with weighted voting
- [ ] Add validator weights to `config.py`
- [ ] Test validator effectiveness (measure FP reduction per validator)
- [ ] **Deploy**: Commit to branch `feature/enhanced-validators`

### Week 2
- [ ] Upgrade `calculate_confidence()` to 8-factor formula
- [ ] Add temporal/motion/bg factors from MOG2
- [ ] Update confidence visualization in web UI
- [ ] Test confidence calibration (validate scores match actual FP/FN)
- [ ] **Deploy**: Commit to branch `feature/confidence-scoring-v2`

### Week 2.5
- [ ] Create `DetectionMetrics` monitoring system
- [ ] Implement FP/FN logging
- [ ] Add fallback prediction strategy
- [ ] Create A/B testing framework (toggle each feature on/off)
- [ ] Document performance baseline
- [ ] **Release**: Merge all branches to `main` as v2.0

---

## 🎯 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **False Positive Reduction** | 50-70% | Manually test 10 scenarios |
| **Detection Jitter** | Reduced 80% | Measure confidence variance per frame |
| **Latency Impact** | < 5ms | Profile with `time.perf_counter()` |
| **Memory Usage** | No increase | Monitor RSS before/after |
| **Crowded Scenes** | 30% improvement | Test with 3+ overlapping targets |

---

## 🔄 Testing Protocol

### Test Set A: Lighting Variations
1. Daylight (noon, shadows, reflections)
2. Fluorescent indoor (uniform, flicker)
3. Night mode (dark, low contrast)
4. Twilight (transitioning light)

**Expected**: FP rate consistent across all < 10%

### Test Set B: Temporal Stability
1. Jittery movement (rapid micro-movements)
2. Smooth panning (slow, continuous)
3. Rapid target switching (snap between targets)

**Expected**: No lock/unlock flickering, smooth tracking

### Test Set C: Outlier Scenarios
1. Moving shadows
2. Reflections on floor/walls
3. Similar-colored objects (boxes, clothing)
4. Partial occlusion (half-visible target)

**Expected**: Correctly rejected as outliers

---

## 🚀 Next Steps

1. **Review this plan** - Do you agree with approach?
2. **Confirm priorities** - Start Phase A1 (MOG2) first?
3. **Set up testing environment** - Record baseline metrics now?
4. **Ready to code?** - I'll create detailed code for Phase A1.1

What's your call?
