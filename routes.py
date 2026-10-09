# -*- coding: utf-8 -*-
import numpy as np
from flask import Flask, jsonify, send_from_directory, request
from config import config
import arduino as ard
import vision
import secrets
import functools
import os
import math
import re

app = Flask(__name__, template_folder="templates")

TOKEN_FILE = ".api_token"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        API_TOKEN = f.read().strip()
else:
    API_TOKEN = secrets.token_hex(16)
    with open(TOKEN_FILE, "w") as f:
        f.write(API_TOKEN)
    os.chmod(TOKEN_FILE, 0o600)

print("[TOKEN] API Token: {}...".format(API_TOKEN[:8]))

def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-API-Token", "")
        if not secrets.compare_digest(token, API_TOKEN):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

class ValidationError(Exception): pass

def _int(d, k, lo=None, hi=None):
    if k not in d: return None
    try: v = int(d[k])
    except: raise ValidationError("'{}' must be int".format(k))
    if lo is not None and v < lo: raise ValidationError("'{}' min {}".format(k, lo))
    if hi is not None and v > hi: raise ValidationError("'{}' max {}".format(k, hi))
    return v

def _float(d, k, lo=None, hi=None):
    if k not in d: return None
    try: v = float(d[k])
    except: raise ValidationError("'{}' must be number".format(k))
    if not math.isfinite(v): raise ValidationError("'{}' must be finite".format(k))
    if lo is not None and v < lo: raise ValidationError("'{}' min {}".format(k, lo))
    if hi is not None and v > hi: raise ValidationError("'{}' max {}".format(k, hi))
    return v

def _str(d, k, choices=None):
    if k not in d: return None
    v = str(d[k]).strip()
    if not v: raise ValidationError("'{}' empty".format(k))
    if choices and v not in choices:
        raise ValidationError("'{}' must be one of {}".format(k, choices))
    return v

def _bool(d, k):
    if k not in d: return None
    v = d[k]
    if isinstance(v, bool): return v
    if isinstance(v, str):
        if v.lower() in ("true","1","yes"): return True
        if v.lower() in ("false","0","no"): return False
    if isinstance(v, int): return bool(v) if v in (0, 1) else None
    raise ValidationError("'{}' must be bool".format(k))

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

@app.route("/status")
def status():
    snap = vision.get_vision_snapshot()
    ard_stats = ard.get_arduino_stats()
    return jsonify({
        "active": snap["active"],
        "arduino": "ok" if ard.arduino and ard.arduino.is_open else "err",
        "fps": snap["fps"],
        "targets": snap["target_count"],
        "aim_zone": vision.AIM_ZONE,
        "show_monitor": snap["show_monitor"],
        "show_win": snap["show_monitor"],
        "show_fov": snap["show_fov"],
        "smooth": config.SMOOTH,
        "screen_w": config.SCREEN_WIDTH,
        "screen_h": config.SCREEN_HEIGHT,
        "lock_lost": snap["lock_lost"],
        "locked": snap["lock_lost"] == 0 and snap["lock_bbox"] is not None,
        "lock_vx": round(snap["lock_vx"], 2),
        "lock_vy": round(snap["lock_vy"], 2),
        "profile": config.ACTIVE_PROFILE,
        "profiles": config.list_profiles(),
        "x_speed": config.X_SPEED,
        "y_speed": config.Y_SPEED,
        "fov": config.FOV,
        "offset_x": config.OFFSET_X,
        "offset_y": config.OFFSET_Y,
        "trigger_delay": config.TRIGGER_DELAY,
        "activation_key": config.ACTIVATION_KEY,
        "trigger_key": config.TRIGGER_KEY,
        "rcs_enable": config.RCS_ENABLE,
        "rcs_strength": config.RCS_STRENGTH,
        "humanize": config.HUMANIZE,
        "human_str": config.HUMAN_STR,
        "use_sim": config.USE_SIMILARITY,
        "trg_zone": config.TRG_ZONE_ON,
        "trg_zone_size": config.TRG_ZONE_SIZE,
        "consecutive_errors": snap["consecutive_errors"],
        "hardware_critical": snap["error_threshold_hit"],
        "dropped_packets": ard_stats["dropped_packets"],
    })

@app.route("/toggle", methods=["POST"])
@require_auth
def toggle():
    new_state = vision.toggle_active()
    return jsonify({"ok": True, "active": new_state})

@app.route("/toggle_monitor", methods=["POST"])
@require_auth
def toggle_monitor():
    new_state = vision.toggle_show_monitor()
    return jsonify({"ok": True, "show_monitor": new_state, "show_win": new_state})

@app.route("/toggle_fov", methods=["POST"])
@require_auth
def toggle_fov():
    new_state = vision.toggle_show_fov()
    return jsonify({"ok": True, "show_fov": new_state})

@app.route("/set_zone", methods=["POST"])
@require_auth
def set_zone():
    z = (request.get_json(silent=True) or {}).get("zone", "head")
    if z in vision.AIM_ZONE_MAP:
        vision.AIM_ZONE = z
        return jsonify({"ok": True, "zone": z})
    return jsonify({"ok": False, "zone": z}), 400

@app.route("/zone", methods=["POST"])
@require_auth
def zone():
    z = (request.get_json(silent=True) or {}).get("zone", "head")
    if z in vision.AIM_ZONE_MAP:
        vision.AIM_ZONE = z
        return jsonify({"ok": True, "zone": z})
    return jsonify({"ok": False, "zone": z}), 400

@app.route("/update", methods=["POST"])
@require_auth
def update():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"status": "error", "ok": False, "message": "JSON required"}), 400
    
    key_map = {
        "spd_x": "x_speed", "spd_y": "y_speed",
        "hum_str": "human_str",
        "off_x": "offset_x", "off_y": "offset_y",
        "trig_ms": "trigger_delay",
        "rcs_on": "rcs_enable", "rcs_str": "rcs_strength",
        "aim_key": "activation_key",
        "trig_key": "trigger_key",
        "com": "serial_port",
    }
    
    data = dict(data)
    for frontend_key, backend_key in key_map.items():
        if frontend_key in data and backend_key not in data:
            data[backend_key] = data.pop(frontend_key)
    
    try:
        fov = _int(data, "fov", 40, 600)
        min_area = _int(data, "min_area", 1, 50000)
        max_area = _int(data, "max_area", 1, 200000)
        if max_area is not None and min_area is not None:
            if max_area <= min_area: raise ValidationError("max_area must > min_area")

        x_speed = _float(data, "x_speed", 0.05, 3.0)
        y_speed = _float(data, "y_speed", 0.05, 3.0)
        smooth = _float(data, "smooth", 0.5, 20.0)
        offset_x = _int(data, "offset_x", -200, 200)
        offset_y = _int(data, "offset_y", -200, 200)

        activation_key = _str(data, "activation_key",
            ["always","alt","shift","ctrl","capslock","tab","x","z","c","v","f","g","e","r","q","mouse1","mouse2","mouse4","mouse5"])

        trigger_key = _str(data, "trigger_key",
            ["mouse1","mouse2","mouse4","mouse5","f","g","v","z","e","r","c","q","x","tab","shift","ctrl","capslock"])

        trigger_delay = _int(data, "trigger_delay", 0, 2000)
        rcs_enable = _bool(data, "rcs_enable")
        rcs_strength = _float(data, "rcs_strength", 0, 30)
        trg_zone_on = _bool(data, "trg_zone_on")
        trg_zone_size = _int(data, "trg_zone_size", 1, 40)
        use_similarity = _bool(data, "use_similarity")
        humanize = _bool(data, "humanize")
        human_str = _float(data, "human_str", 0.1, 10)
        serial_port = _str(data, "serial_port")

        if fov is not None: config.FOV = fov
        if min_area is not None: config.MIN_AREA = min_area
        if max_area is not None: config.MAX_AREA = max_area
        if x_speed is not None: config.X_SPEED = x_speed
        if y_speed is not None: config.Y_SPEED = y_speed
        if smooth is not None: config.SMOOTH = smooth
        if offset_x is not None: config.OFFSET_X = offset_x
        if offset_y is not None: config.OFFSET_Y = offset_y
        if activation_key: config.ACTIVATION_KEY = activation_key
        if trigger_key: config.TRIGGER_KEY = trigger_key
        if trigger_delay is not None: config.TRIGGER_DELAY = trigger_delay
        if rcs_enable is not None: config.RCS_ENABLE = rcs_enable
        if rcs_strength is not None: config.RCS_STRENGTH = rcs_strength
        if trg_zone_on is not None: config.TRG_ZONE_ON = trg_zone_on
        if trg_zone_size is not None: config.TRG_ZONE_SIZE = trg_zone_size
        if use_similarity is not None: config.USE_SIMILARITY = use_similarity
        if humanize is not None: config.HUMANIZE = humanize
        if human_str is not None: config.HUMAN_STR = human_str
        if serial_port: config.SERIAL_PORT = serial_port

        if "color" in data: _apply_color(str(data["color"]))

        config.save()
        return jsonify({"status": "ok", "ok": True})

    except ValidationError as e:
        return jsonify({"status": "error", "ok": False, "message": str(e)}), 422
    except Exception as e:
        print("[ERROR] Update: {}".format(e))
        return jsonify({"status": "error", "ok": False, "message": str(e)}), 500

@app.route("/reconnect", methods=["POST"])
@require_auth
def reconnect():
    ok = ard.connect_arduino()
    return jsonify({"ok": ok})

@app.route("/profile/switch", methods=["POST"])
@require_auth
def profile_switch():
    name = str((request.get_json(silent=True) or {}).get("name", "")).strip()
    if not name or not re.match(r"^[A-Za-z0-9_\-]{1,32}$", name):
        return jsonify({"ok": False, "message": "invalid name"}), 400
    if name not in config.list_profiles():
        return jsonify({"ok": False, "message": "profile not found"}), 404
    config.switch_profile(name)
    return jsonify({"ok": True, "profile": name})

@app.route("/profile/save", methods=["POST"])
@require_auth
def profile_save():
    name = str((request.get_json(silent=True) or {}).get("name", config.ACTIVE_PROFILE)).strip()
    if not name or not re.match(r"^[A-Za-z0-9_\-]{1,32}$", name):
        return jsonify({"ok": False, "message": "invalid name"}), 400
    config.save(name)
    return jsonify({"ok": True, "profile": name})

_COLOR_MAP = {
    "9900ff": ([130,60,70], [175,255,255]),
    "ffff00": ([25,150,150], [35,255,255]),
    "00ffff": ([85,150,150], [95,255,255]),
    "ff00ff": ([140,150,150],[160,255,255]),
    "ff0000": ([0,150,150], [10,255,255]),
    "ffaa00": ([10,150,150], [25,255,255]),
    "00ff00": ([50,150,150], [70,255,255]),
    "0088ff": ([100,150,100],[120,255,255]),
}

def _apply_color(hex_str):
    key = hex_str.lstrip("#").lower()
    if key in _COLOR_MAP:
        lo, hi = _COLOR_MAP[key]
        config.LOWER_COLOR = np.array(lo)
        config.UPPER_COLOR = np.array(hi)
        # NOTE: Don't call config.save() here — the caller /update already saves
        print("[COLOR] {}".format(key))
    else:
        print("[WARN] Unknown color: {}".format(key))
