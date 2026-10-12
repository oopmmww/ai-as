#!/usr/bin/env python
"""Test script to verify all imports work correctly"""

import sys
import os

# Ensure project root is in sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

print("=" * 60)
print("[TEST] Verifying all imports...")
print("=" * 60)

try:
    print("\n[1] Testing src.config...")
    from src.config import config, initialize_rcs_learner, get_rcs_learner
    print("    [OK] config imported")
    print(f"    - SERIAL_PORT: {config.SERIAL_PORT}")
    print(f"    - FOV: {config.FOV}")
    
    print("\n[2] Testing src.core...")
    from src.core import arduino as ard, vision_loop, get_vision_snapshot
    print("    [OK] arduino, vision_loop imported")
    print(f"    - arduino.find_arduino_port: {ard.find_arduino_port}")
    
    print("\n[3] Testing src.logging...")
    from src.logging import initialize_logger, get_logger, register_logger_routes
    from src.logging import data_logger
    print("    [OK] logging modules imported")
    
    print("\n[4] Testing src.web...")
    from src.web import app, register_dashboard_route
    print("    [OK] Flask app imported")
    
    print("\n[5] Testing data_logger convenience functions...")
    data_logger.log_event('test', 'info', 'Test message', {})
    print("    [OK] log_event() works")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All imports verified!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
