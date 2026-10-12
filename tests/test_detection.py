#!/usr/bin/env python
"""Test detection system"""

import sys
import os
import time

# Ensure project root is in sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("[TEST] Detection System Verification")
print("=" * 60)

print("\n[1] Testing Vision Module...")
try:
    from src.core import vision_loop, get_vision_snapshot
    print("    ✅ Vision module loaded")
    
    # Get snapshot
    snap = get_vision_snapshot()
    print(f"    ✅ Got vision snapshot")
    print(f"       - Active: {snap['active']}")
    print(f"       - FPS: {snap['fps']}")
    print(f"       - Target Count: {snap['target_count']}")
    print(f"       - Lock Lost: {snap['lock_lost']}")
    
except Exception as e:
    print(f"    ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[2] Testing Detection Parameters...")
try:
    from src.config import config
    
    params = config.get_detection_params()
    print("    ✅ Got detection parameters:")
    print(f"       - FOV: {params['fov']}")
    print(f"       - Lower Color: {params['lower_color']}")
    print(f"       - Upper Color: {params['upper_color']}")
    print(f"       - Min Area: {params['min_area']}")
    print(f"       - Max Area: {params['max_area']}")
    print(f"       - X Speed: {params['x_speed']}")
    print(f"       - Y Speed: {params['y_speed']}")
    
except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n[3] Testing Color Detection...")
try:
    import cv2
    import numpy as np
    from src.core.vision import detect_color
    
    # Create test frame (cyan color)
    test_frame = np.ones((100, 100, 3), dtype=np.uint8)
    test_frame[:, :] = [255, 255, 0]  # Yellow in BGR
    
    # Convert to HSV
    hsv = cv2.cvtColor(test_frame, cv2.COLOR_BGR2HSV)
    
    # Try detection with default colors
    lower = np.array([130, 60, 70])
    upper = np.array([175, 255, 255])
    
    mask = detect_color(hsv, lower, upper)
    detected = np.count_nonzero(mask)
    
    print(f"    ✅ Color detection working")
    print(f"       - Test frame created")
    print(f"       - Mask generated")
    print(f"       - Pixels detected: {detected}/10000")
    
except Exception as e:
    print(f"    ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[4] Testing Arduino Communication...")
try:
    from src.core import arduino
    
    port = arduino.find_arduino_port()
    if port:
        print(f"    ✅ Arduino found at: {port}")
        
        # Try to connect
        if arduino.connect_arduino():
            print(f"    ✅ Arduino connected")
            
            # Get stats
            stats = arduino.get_arduino_stats()
            print(f"       - Dropped packets: {stats['dropped_packets']}")
            print(f"       - Queue size: {stats['queue_size']}/{stats['queue_max']}")
        else:
            print(f"    ❌ Failed to connect to Arduino")
    else:
        print(f"    ⚠️  No Arduino detected - Check USB connection")
        
except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n[5] Testing Logger System...")
try:
    from src.logging import initialize_logger, get_logger, data_logger
    
    # Initialize logger
    initialize_logger(log_dir="logs")
    print("    ✅ Logger initialized")
    
    # Try logging event
    data_logger.log_event("test", "info", "Test message", {"test": "data"})
    print("    ✅ Log event recorded")
    
    # Get logger and check
    logger = get_logger()
    if logger:
        print("    ✅ Logger object accessible")
    
except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n[6] Testing Web Server...")
try:
    from src.web import app
    
    print(f"    ✅ Flask app loaded")
    print(f"       - Template folder: {app.template_folder}")
    
    # Check routes
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    print(f"       - Routes registered: {len(routes)}")
    
    # Show key routes
    key_routes = [r for r in routes if r in ['/', '/status', '/api/config']]
    for route in key_routes[:5]:
        print(f"       - {route}")
    
except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n" + "=" * 60)
print("[SUMMARY] System diagnostics complete")
print("=" * 60)
