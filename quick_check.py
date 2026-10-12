#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick system check - no emoji"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("[CHECK] Quick System Test")
print("="*60)

try:
    print("\n[1] Testing imports...")
    from src.core import vision_loop, get_vision_snapshot
    from src.config import config
    from src.core import arduino
    print("    OK: Imports working")
    
    print("\n[2] Testing Arduino...")
    port = arduino.find_arduino_port()
    if port:
        print(f"    OK: Arduino found at {port}")
    else:
        print(f"    ERROR: No Arduino detected")
    
    print("\n[3] Testing vision snapshot...")
    snap = get_vision_snapshot()
    print(f"    OK: Snapshot retrieved")
    print(f"       Active: {snap['active']}")
    print(f"       FPS: {snap['fps']}")
    print(f"       Targets: {snap['target_count']}")
    
    print("\n[4] Testing config...")
    print(f"    OK: FOV={config.FOV}")
    print(f"       Color lower: {config.LOWER_COLOR}")
    print(f"       Color upper: {config.UPPER_COLOR}")
    
    print("\n[5] Testing web server...")
    from src.web import app
    print(f"    OK: Flask app loaded")
    print(f"       Template: {app.template_folder}")
    print(f"       Routes: {len(list(app.url_map.iter_rules()))}")
    
    print("\n" + "="*60)
    print("[RESULT] System operational")
    print("="*60)
    
except Exception as e:
    print(f"\n    ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
