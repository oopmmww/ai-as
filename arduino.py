import serial, serial.tools.list_ports
import time, threading, queue
from config import config

arduino         = None
_q              = queue.Queue(maxsize=8)
_alive          = False
_sender_lock    = threading.Lock()     # protects _alive, _last_send_ms
_lock           = threading.Lock()     # protects arduino serial object
_stats_lock     = threading.Lock()     # protects counters (_dropped_packets, _queue_overflow_warn)
_last_send_ms   = 0.0
_dropped_packets = 0
_consecutive_reconnect_failures = 0
_queue_overflow_warn = 0
_reconnect_scheduled = False
_reconnect_lock = threading.Lock()
HEARTBEAT_MS    = 200
RECONNECT_DELAY = 2

# ─── Port Detection ─────────────────────────────────────
def find_arduino_port():
    for p in serial.tools.list_ports.comports():
        if any(k in p.description.lower() for k in
               ["arduino","ch340","ch341","usb-serial","uart"]):
            print("[ARDUINO] Found: {} ({})".format(p.device, p.description))
            return p.device
    ports = serial.tools.list_ports.comports()
    if ports:
        print("[ARDUINO] Using: {}".format(ports[0].device))
        return ports[0].device
    return None

# ─── Connect ────────────────────────────────────────────
def connect_arduino():
    global arduino
    with _lock:
        try:
            if arduino and arduino.is_open: arduino.close()
            if not config.SERIAL_PORT: arduino = None; return False
            arduino = serial.Serial(
                config.SERIAL_PORT, config.SERIAL_BAUD,
                timeout=0.1, write_timeout=0.1)
            time.sleep(1.8)
            print("[ARDUINO] OK @ {}".format(config.SERIAL_PORT))
            return True
        except serial.SerialException as e:
            print("[ARDUINO] Connect failed: {}".format(e))
            arduino = None; return False

# ─── Write ──────────────────────────────────────────────
def _write(dx: int, dy: int) -> bool:
    global _reconnect_scheduled
    try:
        with _lock:
            if not arduino or not arduino.is_open: return False
            arduino.write(f"{dx},{dy}\n".encode())
        return True
    except serial.SerialException:
        with _reconnect_lock:
            if not _reconnect_scheduled:
                _reconnect_scheduled = True
                threading.Thread(
                    target=_schedule_reconnect,
                    daemon=True,
                    name="ArdReconnect"
                ).start()
        return False
    except Exception as e:
        print("[ERROR] Write: {}".format(e)); return False

def _schedule_reconnect():
    global _reconnect_scheduled
    time.sleep(RECONNECT_DELAY)
    connect_arduino()
    _reconnect_scheduled = False

# ─── Sender Thread ──────────────────────────────────────
def _sender():
    global _alive, _last_send_ms
    _last_send_ms = time.perf_counter() * 1000
    while _alive:
        try:
            try:
                dx, dy = _q.get(timeout=HEARTBEAT_MS/1000)
            except queue.Empty:
                dx = dy = None
            now = time.perf_counter() * 1000
            if dx is not None:
                _write(dx, dy); _last_send_ms = now
            elif now - _last_send_ms >= HEARTBEAT_MS:
                _write(0, 0); _last_send_ms = now
        except Exception as e:
            print("[ERROR] Sender: {}".format(e))

# ─── Public API ─────────────────────────────────────────
def send_to_arduino(dx: int, dy: int) -> bool:
    """
    Send movement to Arduino. Returns True if successfully queued AND Arduino is open,
    False if Arduino is disconnected (triggers mouse fallback).
    """
    global _queue_overflow_warn, _dropped_packets
    if not _alive:
        return False
    
    # Check Arduino connection status FIRST
    with _lock:
        arduino_ok = (arduino is not None and arduino.is_open)
    
    if not arduino_ok:
        # Arduino not connected - fallback will handle this
        return False
    
    try:
        if _q.full():
            try:
                old_dx, old_dy = _q.get_nowait()
                dx += old_dx
                dy += old_dy
                with _stats_lock:
                    _queue_overflow_warn += 1
                    _dropped_packets += 1
                    overflow_count = _queue_overflow_warn
                if overflow_count % 20 == 0:
                    print("[WARN] Queue overflow (merged {}x)".format(overflow_count))
            except queue.Empty:
                pass
        _q.put_nowait((dx, dy))
        return True  # Successfully queued AND Arduino open
    except Exception as e:
        print("[ERROR] Send: {}".format(e))
        return False

def get_arduino_stats():
    """Return Arduino communication statistics (thread-safe)."""
    with _stats_lock:
        dp = _dropped_packets
        rcf = _consecutive_reconnect_failures
    return {
        "dropped_packets": dp,
        "queue_size": _q.qsize(),
        "queue_max": _q.maxsize,
        "consecutive_reconnect_failures": rcf,
    }

def start_sender():
    global _alive
    _alive = True
    threading.Thread(target=_sender, daemon=True, name="ArdSender").start()
    print("[SENDER] Started")

def stop_sender():
    global _alive; _alive = False