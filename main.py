import threading, webbrowser, time, sys, ctypes, atexit
import gc
import arduino as ard
from vision import vision_loop
from routes import app
import keyboard
from data_logger import initialize_logger, get_logger
from logger_routes import register_logger_routes
from dashboard_route import register_dashboard_route
from rcs_learner import initialize_rcs_learner, get_rcs_learner

_shutdown_event = threading.Event()
_cleanup_done   = False          # guard ป้องกัน double-cleanup (atexit + kill_listener)

def _preflight_checks():
    """Verify camera and Arduino availability before starting."""
    print("\n[PRE-FLIGHT] Starting hardware checks...")
    
    # Camera check
    try:
        import cv2
        import numpy as np
        try:
            import dxcam as _dx
            print("  [OK] dxcam available")
        except:
            try:
                import mss as _mss
                sc = _mss.mss()
                mon = sc.monitors[1]  # Primary monitor
                frame = sc.grab(mon)
                if frame is not None:
                    print("  [OK] Camera (mss) responsive")
                else:
                    print("  [WARN] Camera (mss) not responsive")
            except Exception as ce:
                print("  [WARN] Camera check failed: {}".format(ce))
    except Exception as e:
        print("  [WARN] Camera check failed: {}".format(e))
    
    # Arduino check
    try:
        import serial
        import serial.tools.list_ports
        
        ports = serial.tools.list_ports.comports()
        if not ports:
            print("  [WARN] No serial ports found")
        else:
            # Try to connect to configured port
            port = ard.config.SERIAL_PORT or "COM3"
            try:
                test_conn = serial.Serial(port, 115200, timeout=0.5)
                test_conn.close()
                print(f"  [OK] Arduino ({port}) responsive")
            except Exception as ae:
                print(f"  [WARN] Arduino ({port}) not responsive: {ae}")
    except Exception as e:
        print(f"  [WARN] Arduino check failed: {e}")
    
    print()

def _hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd: ctypes.windll.user32.ShowWindow(hwnd, 0)
    except: pass

def _cleanup():
    """Graceful shutdown: stop threads and close resources.
    
    Guard ด้วย _cleanup_done เพราะถูกเรียกได้ 2 ทาง:
    1. atexit.register(_cleanup)
    2. _kill_listener → _cleanup() → sys.exit() → trigger atexit อีกรอบ
    """
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True

    print("\n[SHUTDOWN] Graceful shutdown initiated...")
    _shutdown_event.set()
    time.sleep(0.5)
    ard.stop_sender()
    try:
        if ard.arduino and ard.arduino.is_open:
            ard.arduino.close()
            print("  [OK] Serial port closed")
    except Exception as e:
        print(f"  [WARN] Error closing serial: {e}")
    
    # Save logger data
    try:
        logger = get_logger()
        if logger:
            logger.stop_and_save()
            print("  [OK] Logger data saved (JSON)")
            
            # Export CSV for analysis
            if logger.export_csv():
                print("  [OK] Logger data exported (CSV)")
            else:
                print("  [WARN] CSV export failed")
    except Exception as e:
        print(f"  [WARN] Error saving logger: {e}")
    
    # Phase 4.3: Save RCS patterns
    try:
        rcs = get_rcs_learner()
        if rcs:
            rcs.save_patterns()
            print("  [OK] RCS patterns saved")
    except Exception as e:
        print(f"  [WARN] Error saving RCS: {e}")
    
    print("[OK] Shutdown complete")

def _kill_listener():
    keyboard.wait("end")
    _cleanup()
    sys.exit(0)

def _open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000/dashboard")
    print("[BROWSER] Opened at http://127.0.0.1:5000/dashboard")

def _gc_tuning_loop():
    """Phase 3.2: GC tuning - manually trigger collection to avoid pauses in vision loop"""
    # Disable automatic GC to prevent pauses during vision loop
    gc.disable()
    print("[GC] Garbage collection disabled (manual control)")
    
    while not _shutdown_event.is_set():
        time.sleep(2.0)  # Trigger every 2 seconds (off-thread)
        try:
            collected = gc.collect()
            if collected > 100:  # Only log if significant collection happened
                print(f"[GC] Collected {collected} objects")
        except Exception as e:
            print(f"[GC] Error: {e}")

if __name__ == "__main__":
    _hide_console()
    print("=" * 50)
    print("[STARTUP] Aimbot starting... Press END to kill")
    print("=" * 50)

    # Register cleanup handler
    atexit.register(_cleanup)

    # Pre-flight checks
    _preflight_checks()

    # Arduino
    ard.config.SERIAL_PORT = ard.find_arduino_port() or "COM3"
    ard.connect_arduino()
    ard.start_sender()

    # Vision thread
    threading.Thread(target=vision_loop,    daemon=True, name="VisionLoop").start()

    # Browser
    threading.Thread(target=_open_browser,  daemon=True, name="Browser").start()
    
    # Phase 3.2: GC tuning thread (avoid pauses in vision loop)
    threading.Thread(target=_gc_tuning_loop, daemon=True, name="GCTuning").start()

    # Kill key listener (NOT daemon, so it keeps program alive)
    threading.Thread(target=_kill_listener, daemon=False, name="KillListener").start()

    # Logger initialization
    initialize_logger(log_dir="logs")
    
    # Phase 4.3: RCS Learner initialization
    initialize_rcs_learner()
    print("[STARTUP] RCS learner initialized")
    
    # Register logger routes
    register_logger_routes(app)
    
    # Register dashboard route
    register_dashboard_route(app)
    
    # Flask (main thread)
    try:
        app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        _cleanup()