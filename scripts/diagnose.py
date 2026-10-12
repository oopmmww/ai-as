#!/usr/bin/env python
"""
AIAS Diagnostic Tool
ตรวจสอบสถานะระบบ Hardware Dependencies และ Configuration
"""

import sys
import os
import json
from pathlib import Path

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_status(name, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"  {status_icon} {name:<40} {details}")

def check_python_version():
    print_header("1. Python Version")
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 7)
    print_status("Python Version", ok, f"{version}")
    return ok

def check_directory():
    print_header("2. Project Directory")
    cwd = os.getcwd()
    ok = os.path.exists("main.py") and os.path.exists("src")
    print_status("Working Directory", ok, cwd)
    print_status("main.py exists", os.path.exists("main.py"))
    print_status("src/ exists", os.path.exists("src"))
    print_status("templates/ exists", os.path.exists("templates"))
    print_status("logs/ exists", os.path.exists("logs"))
    return ok

def check_imports():
    print_header("3. Module Imports")
    
    modules = [
        ("src.config", "config"),
        ("src.core", "vision_loop, arduino"),
        ("src.logging", "data_logger"),
        ("src.web", "app"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("serial", "pySerial"),
        ("flask", "Flask"),
        ("keyboard", "keyboard"),
        ("psutil", "psutil"),
    ]
    
    all_ok = True
    for module_path, display_name in modules:
        try:
            __import__(module_path)
            print_status(f"Import {display_name}", True, f"({module_path})")
        except ImportError as e:
            print_status(f"Import {display_name}", False, f"Error: {str(e)[:40]}")
            all_ok = False
    
    return all_ok

def check_config():
    print_header("4. Configuration")
    
    try:
        from src.config import config
        
        print_status("Config Loaded", True)
        print(f"\n  Hardware Settings:")
        print(f"    - SERIAL_PORT: {config.SERIAL_PORT}")
        print(f"    - SERIAL_BAUD: {config.SERIAL_BAUD}")
        print(f"    - SCREEN: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}")
        
        print(f"\n  Detection Settings:")
        print(f"    - FOV: {config.FOV}")
        print(f"    - MIN_AREA: {config.MIN_AREA}")
        print(f"    - MAX_AREA: {config.MAX_AREA}")
        
        print(f"\n  Color Range (HSV):")
        lower = config.LOWER_COLOR
        upper = config.UPPER_COLOR
        print(f"    - Lower: H={lower[0]} S={lower[1]} V={lower[2]}")
        print(f"    - Upper: H={upper[0]} S={upper[1]} V={upper[2]}")
        
        print(f"\n  Aim Settings:")
        print(f"    - X_SPEED: {config.X_SPEED}")
        print(f"    - Y_SPEED: {config.Y_SPEED}")
        print(f"    - SMOOTH: {config.SMOOTH}")
        
        return True
    except Exception as e:
        print_status("Config Load", False, str(e)[:50])
        return False

def check_arduino():
    print_header("5. Arduino Connection")
    
    try:
        from src.core import arduino
        
        port = arduino.find_arduino_port()
        if port:
            print_status("Arduino Port Detection", True, port)
            return True
        else:
            print_status("Arduino Port Detection", False, "No ports found")
            print("\n  Available ports:")
            try:
                import serial.tools.list_ports
                for p in serial.tools.list_ports.comports():
                    print(f"    - {p.device}: {p.description}")
            except:
                print("    (Unable to list ports)")
            return False
    except Exception as e:
        print_status("Arduino Check", False, str(e)[:50])
        return False

def check_camera():
    print_header("6. Camera / Screen Capture")
    
    try:
        import cv2
        import numpy as np
        
        # Try dxcam first
        try:
            import dxcam as dx
            cap = dx.ScreenCapture()
            frame = cap.grab()
            cap.__del__()
            print_status("dxcam", True, "Screen capture available")
            return True
        except:
            pass
        
        # Try mss
        try:
            import mss
            sct = mss.mss()
            mon = sct.monitors[1]
            frame = sct.grab(mon)
            print_status("mss (fallback)", True, f"{mon['width']}x{mon['height']}")
            return True
        except Exception as e:
            print_status("Screen Capture", False, str(e)[:50])
            return False
            
    except Exception as e:
        print_status("Camera Check", False, str(e)[:50])
        return False

def check_flask():
    print_header("7. Flask & Web Server")
    
    try:
        from src.web import app
        import flask
        
        print_status("Flask App", True, "Loaded")
        print_status("Flask Version", True, flask.__version__)
        
        # Check port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result == 0:
            print_status("Port 5000 Status", False, "Already in use (another app running?)")
            return False
        else:
            print_status("Port 5000 Status", True, "Available")
            return True
            
    except Exception as e:
        print_status("Flask Check", False, str(e)[:50])
        return False

def check_logging():
    print_header("8. Logging System")
    
    try:
        from src.logging import initialize_logger, get_logger
        
        logs_dir = Path("logs")
        if logs_dir.exists():
            print_status("Logs Directory", True, str(logs_dir.absolute()))
            
            # Count log files
            json_files = list(logs_dir.glob("session_*.json"))
            csv_files = list(logs_dir.glob("detections_*.csv"))
            print(f"\n  Log files on disk:")
            print(f"    - JSON sessions: {len(json_files)}")
            print(f"    - CSV detections: {len(csv_files)}")
            
            if json_files:
                latest = sorted(json_files)[-1]
                size = latest.stat().st_size / 1024
                print(f"    - Latest: {latest.name} ({size:.1f} KB)")
        else:
            print_status("Logs Directory", False, "Directory not found")
            print("  Creating logs/ directory...")
            logs_dir.mkdir(parents=True, exist_ok=True)
            print_status("Logs Directory", True, "Created")
        
        return True
    except Exception as e:
        print_status("Logging Check", False, str(e)[:50])
        return False

def check_profiles():
    print_header("9. Configuration Profiles")
    
    try:
        from src.config import config
        
        profiles = config.list_profiles()
        print_status("Profiles Found", True, f"{len(profiles)} profile(s)")
        
        for i, profile in enumerate(profiles, 1):
            marker = "→" if profile == config.ACTIVE_PROFILE else " "
            print(f"    {marker} [{i}] {profile}")
        
        print(f"\n  Active Profile: {config.ACTIVE_PROFILE}")
        return True
    except Exception as e:
        print_status("Profiles Check", False, str(e)[:50])
        return False

def check_dependencies():
    print_header("10. Additional Dependencies")
    
    optional = [
        ("noise", "Perlin noise (for better humanize)"),
        ("psutil", "System monitoring"),
        ("pyautogui", "Mouse control (NOT USED - Arduino only)"),
    ]
    
    for module_name, description in optional:
        try:
            __import__(module_name)
            print_status(module_name, True, description)
        except ImportError:
            print_status(module_name, False, f"Missing - {description}")

def main():
    print("\n")
    print("=" * 60)
    print("  AIAS Diagnostic Tool v1.0")
    print("  System Status Report")
    print("=" * 60)
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python_version()))
    results.append(("Project Directory", check_directory()))
    results.append(("Module Imports", check_imports()))
    results.append(("Configuration", check_config()))
    results.append(("Arduino", check_arduino()))
    results.append(("Camera/Capture", check_camera()))
    results.append(("Flask/Web", check_flask()))
    results.append(("Logging", check_logging()))
    results.append(("Profiles", check_profiles()))
    check_dependencies()
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    print(f"  Checks Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🟢 System Status: READY TO RUN")
        print("\n  Next step: python main.py")
        return 0
    else:
        print("\n  🟠 System Status: ISSUES FOUND")
        print("\n  Failed checks:")
        for name, ok in results:
            if not ok:
                print(f"    - {name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
