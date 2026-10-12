#!/usr/bin/env python
"""Debug color detection"""

import sys
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("[DEBUG] Color Detection Test")
print("=" * 60)

# Create test frames with different colors in BGR
print("\n[1] Creating test frames...")

# Test 1: Yellow (BGR: 0,255,255)
yellow_frame = np.ones((100, 100, 3), dtype=np.uint8)
yellow_frame[:, :] = [0, 255, 255]  # Yellow in BGR

# Test 2: Cyan (BGR: 255,255,0)
cyan_frame = np.ones((100, 100, 3), dtype=np.uint8)
cyan_frame[:, :] = [255, 255, 0]  # Cyan in BGR

# Test 3: Red (BGR: 0,0,255)
red_frame = np.ones((100, 100, 3), dtype=np.uint8)
red_frame[:, :] = [0, 0, 255]  # Red in BGR

print("    ✅ Test frames created")

# Convert to HSV
print("\n[2] Converting to HSV...")
yellow_hsv = cv2.cvtColor(yellow_frame, cv2.COLOR_BGR2HSV)
cyan_hsv = cv2.cvtColor(cyan_frame, cv2.COLOR_BGR2HSV)
red_hsv = cv2.cvtColor(red_frame, cv2.COLOR_BGR2HSV)

# Get sample HSV values
y_sample = yellow_hsv[0, 0]
c_sample = cyan_hsv[0, 0]
r_sample = red_hsv[0, 0]

print(f"    Yellow HSV: {y_sample}")
print(f"    Cyan HSV:   {c_sample}")
print(f"    Red HSV:    {r_sample}")

# Current config
lower_config = np.array([130, 60, 70])
upper_config = np.array([175, 255, 255])

print(f"\n[3] Current Config Range:")
print(f"    Lower: {lower_config}")
print(f"    Upper: {upper_config}")

# Test detection
print("\n[4] Testing detection with current config...")

for name, frame_hsv, sample in [("Yellow", yellow_hsv, y_sample),
                                 ("Cyan", cyan_hsv, c_sample),
                                 ("Red", red_hsv, r_sample)]:
    mask = cv2.inRange(frame_hsv, lower_config, upper_config)
    detected = np.count_nonzero(mask)
    print(f"    {name} ({sample}): {detected}/10000 pixels")

# Try with different ranges
print("\n[5] Testing with adjusted ranges...")

# For yellow-ish colors (low saturation tolerance)
lower_yellow = np.array([25, 30, 30])    # Wider yellow range
upper_yellow = np.array([35, 255, 255])

mask = cv2.inRange(yellow_hsv, lower_yellow, upper_yellow)
detected = np.count_nonzero(mask)
print(f"    Yellow with range {lower_yellow}-{upper_yellow}: {detected}/10000 pixels")

# For red colors
lower_red1 = np.array([0, 60, 60])
upper_red1 = np.array([20, 255, 255])
lower_red2 = np.array([170, 60, 60])
upper_red2 = np.array([180, 255, 255])

mask1 = cv2.inRange(red_hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(red_hsv, lower_red2, upper_red2)
mask = cv2.bitwise_or(mask1, mask2)
detected = np.count_nonzero(mask)
print(f"    Red (with wrap): {detected}/10000 pixels")

print("\n[RECOMMENDATION]")
print("    Current config (130-175 Hue) detects:")
print("    - Purples/Magentas well")
print("    - Reds poorly (need wrap-around)")
print("    ")
print("    For better detection, adjust via dashboard:")
print("    Settings → Color Detection → Adjust sliders")
print("    " + "=" * 60)
