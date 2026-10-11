# 🎯 AIAS - AI Aimbot System

**Status**: ✅ **ระบบพร้อมใช้งาน**

---

## 📖 เอกสารประกอบ

| เอกสาร | คำอธิบาย | ผู้อ่าน |
|--------|---------|--------|
| **QUICK_START.md** | 🚀 วิธีเริ่มต้นใช้งาน | ผู้ใช้ใหม่ |
| **SYSTEM_ANALYSIS.md** | 📊 วิเคราะห์ระบบ + Architecture | นักพัฒนา |
| **README_TH.md** | 📖 ไฟล์นี้ - ภาพรวมระบบ | ทุกคน |

---

## 🎬 เริ่มต้น (3 ขั้นตอนง่าย ๆ)

### ขั้นตอนที่ 1: ตรวจสอบระบบ
```bash
cd c:\Users\kitatar52\Downloads\aias
python diagnose.py
```

**ผลลัพธ์คาดหวัง:**
```
============================================================
  SUMMARY
============================================================

  Checks Passed: 9/9

  🟢 System Status: READY TO RUN
```

### ขั้นตอนที่ 2: เริ่มระบบ
```bash
python main.py
```

**สิ่งที่เกิดขึ้น:**
- ✅ ตรวจสอบ Hardware (Camera, Arduino)
- ✅ เชื่อมต่อกับ Arduino
- ✅ เริ่มต้น Vision Loop
- ✅ เปิด Browser ไปที่ Dashboard

### ขั้นตอนที่ 3: ใช้งาน
```
http://127.0.0.1:5000/
```

---

## ⌨️ ปุ่มควบคุม

| ปุ่ม | ฟังก์ชัน |
|-----|---------|
| **ALT** | ยืนยัน (Activate Aim) |
| **MOUSE1** | ยิง (Trigger Fire) |
| **END** | ปิดโปรแกรม |

---

## 🏗️ โครงสร้างระบบ

```
AIAS System Architecture
│
├─ 🎯 Vision Loop
│  ├─ Grab Screen Frame
│  ├─ Detect Target Color (HSV)
│  ├─ Validate Detection
│  ├─ Calculate Aim (X, Y)
│  ├─ Humanize Movement
│  └─ Send to Arduino
│
├─ 🔌 Arduino Interface
│  ├─ Auto-Detect Serial Port
│  ├─ Serial Communication (115200 baud)
│  ├─ Queue Management
│  └─ Heartbeat/Reconnect
│
├─ ⚙️ Configuration System
│  ├─ Color Detection Range (HSV)
│  ├─ Aim Speed & Smoothing
│  ├─ RCS Learning
│  ├─ Profile Switching
│  └─ JSON Persistence
│
├─ 📊 Logging System
│  ├─ Session Recording
│  ├─ Detection Tracking
│  ├─ Performance Metrics (FPS, Latency)
│  ├─ Event Logging
│  └─ CSV Export
│
└─ 🌐 Web Dashboard
   ├─ System Status
   ├─ Real-time Config
   ├─ Performance Graphs
   └─ Log Viewer
```

---

## 📦 Module Structure

### 1. **src/config/** - ⚙️ Configuration
```python
from src.config import config

# Properties
config.SERIAL_PORT          # COM3
config.FOV                  # 170
config.X_SPEED, Y_SPEED     # 0.35, 0.38
config.LOWER_COLOR          # [H, S, V] lower bound
config.UPPER_COLOR          # [H, S, V] upper bound
config.ACTIVATION_KEY       # 'alt'
config.TRIGGER_KEY          # 'mouse1'
config.RCS_ENABLE           # True/False
config.HUMANIZE             # True/False

# Methods
config.get_detection_params()   # Atomic snapshot
config.save(profile_name)       # Save to JSON
config.load(profile_name)       # Load from JSON
config.switch_profile(name)     # Change profile
config.list_profiles()          # Get all profiles
```

### 2. **src/core/** - 🎯 Vision & Hardware
```python
from src.core import vision_loop, send_to_arduino
from src.core import arduino, find_arduino_port

# Vision
vision_loop()                           # Main vision processing
get_vision_snapshot()                   # Get current frame

# Arduino
find_arduino_port()                     # Auto-detect COM port
connect_arduino()                       # Establish connection
send_to_arduino(dx, dy)                 # Send movement
start_sender(), stop_sender()           # Manage sender thread
get_arduino_stats()                     # Get statistics

# Humanize
humanize_movement(dx, dy)               # Add realistic noise
```

### 3. **src/logging/** - 📝 Data Recording
```python
from src.logging import initialize_logger, get_logger
from src.logging import data_logger

# Initialization
initialize_logger(log_dir="logs")       # Setup logging

# Convenience Functions
data_logger.log_event(
    event_type='detection',
    severity='info',
    message='Target detected',
    data={'x': 100, 'y': 200}
)

data_logger.log_frame(fps=120, latency_ms=8.5)
data_logger.log_environment(frame_number=1000, brightness=0.75)

# Get Logger Object
logger = get_logger()
logger.start_session()
logger.stop_and_save()
logger.export_csv()
```

### 4. **src/web/** - 🌐 Web Interface
```python
from src.web import app, register_dashboard_route

# Flask App
app.run(host="127.0.0.1", port=5000)

# API Endpoints
GET    /                           # Dashboard
POST   /api/config/save            # Save settings
GET    /api/config/load            # Load settings
POST   /api/logger/start           # Start logging
GET    /api/logger/stats           # Get statistics
GET    /api/logger/export          # Export CSV
```

---

## 🔄 Data Flow

### Startup Sequence
```
main.py
├─ preflight_checks()
│  ├─ Check Camera (dxcam/mss)
│  └─ Check Arduino (serial ports)
├─ arduino.find_arduino_port()
├─ arduino.connect_arduino()
├─ arduino.start_sender()
├─ Thread(vision_loop) → daemon=True
├─ Thread(gc_tuning) → daemon=True (Phase 3.2)
├─ Thread(kill_listener) → daemon=False (keeps alive)
├─ initialize_logger(log_dir="logs")
├─ register_logger_routes(app)
├─ register_dashboard_route(app)
└─ app.run() → Flask main thread
```

### Vision Loop (Per Frame)
```
while vision_active:
  ├─ frame = grab_screen()
  ├─ hsv = cv2.cvtColor(frame, BGR2HSV)
  ├─ mask = cv2.inRange(hsv, lower_color, upper_color)
  ├─ contours = cv2.findContours(mask)
  ├─ for contour in contours:
  │  ├─ bbox = validate(contour)
  │  ├─ confidence = calculate_confidence(bbox)
  │  └─ add_to_tracker(bbox)
  ├─ primary = tracker.get_primary_target()
  ├─ IF primary:
  │  ├─ dx, dy = calculate_aim(primary)
  │  ├─ IF humanize: humanize_movement(dx, dy)
  │  ├─ send_to_arduino(dx, dy)
  │  └─ IF trigger: press(TRIGGER_KEY)
  ├─ log_detection(bbox, confidence)
  ├─ log_frame(fps, latency)
  └─ display_frame() if SHOW_MONITOR
```

---

## 🎨 Color Detection Guide

### HSV Color Space
- **H (Hue)**: 0-180 (color: red, green, blue, etc.)
- **S (Saturation)**: 0-255 (color purity: gray to vivid)
- **V (Value)**: 0-255 (brightness: dark to light)

### ตัวอย่าง Color Ranges

| สี | Lower HSV | Upper HSV | หมายเหตุ |
|-----|-----------|-----------|---------|
| Red | [0, 60, 60] | [20, 255, 255] | Target color ทั่วไป |
| Green | [35, 60, 60] | [90, 255, 255] | Alternative target |
| Blue | [100, 60, 60] | [140, 255, 255] | Night mode |

### ปรับค่า Color ผ่าน Dashboard
```
Settings Tab
  ↓
Color Detection
  ├─ Hue Slider (0-180)
  ├─ Sat Slider (0-255)
  ├─ Val Slider (0-255)
  └─ Test Mode (live preview)
```

---

## ⚙️ Configuration Guide

### ไฟล์ Config Location
```
c:\Users\kitatar52\Downloads\aias\aimbot_config.json
```

### ตัวอย่าง JSON
```json
{
  "default": {
    "SERIAL_PORT": "COM3",
    "SERIAL_BAUD": 115200,
    "SCREEN_WIDTH": 1920,
    "SCREEN_HEIGHT": 1080,
    "FOV": 170,
    "MIN_AREA": 5,
    "MAX_AREA": 20000,
    "X_SPEED": 0.35,
    "Y_SPEED": 0.38,
    "SMOOTH": 8.0,
    "OFFSET_X": 0,
    "OFFSET_Y": 0,
    "ACTIVATION_KEY": "alt",
    "TRIGGER_KEY": "mouse1",
    "TRIGGER_DELAY": 50,
    "RCS_ENABLE": false,
    "RCS_STRENGTH": 3.5,
    "TRG_ZONE_ON": false,
    "HUMANIZE": true,
    "HUMAN_STR": 0.5,
    "LOWER_COLOR": [130, 60, 70],
    "UPPER_COLOR": [175, 255, 255],
    "LOGGING_ENABLED": true
  }
}
```

### Recommended Settings

#### ต่ำ CPU Usage (Minimum)
```python
config.FOV = 100           # Smaller detection zone
config.MAX_AREA = 5000     # Limit object size
config.HUMANIZE = False    # Disable noise
config.RCS_ENABLE = False  # Disable RCS
```

#### สูง Accuracy (Maximum)
```python
config.FOV = 200           # Larger detection zone
config.MIN_AREA = 1        # Detect small objects
config.MAX_AREA = 50000    # Allow large objects
config.X_SPEED = 0.5       # Faster response
config.HUMANIZE = True     # Add realism
config.RCS_ENABLE = True   # Learn recoil
```

#### Balanced (Default)
```python
config.FOV = 170
config.X_SPEED = 0.35
config.Y_SPEED = 0.38
config.HUMANIZE = True
config.RCS_ENABLE = False
```

---

## 📊 Performance Metrics

### Expected Performance
- **FPS**: 60-120 FPS (depends on CPU)
- **Latency**: 5-15ms per frame
- **Memory**: ~150-200 MB
- **CPU**: 15-25% (single core)

### Optimization Tips

1. **Reduce FOV** (Detection Zone)
   - Default: 170 → Try: 100-150
   - ลด area ที่ process

2. **Lower MAX_AREA**
   - Default: 20000 → Try: 5000-10000
   - ลดการตรวจจับ noise

3. **Disable Humanize**
   - ลด CPU overhead ~5-10%

4. **Increase Smooth Factor**
   - Default: 8.0 → Try: 12-16
   - ช่วยให้ aim smooth (slower response)

5. **Enable GC Tuning** (Phase 3.2)
   - Automatic (built-in)
   - Prevents FPS drops from garbage collection

---

## 🧪 Testing & Validation

### Test Import Status
```bash
python test_imports.py
```

### Diagnose System
```bash
python diagnose.py
```

### Check Arduino
```bash
python -c "from src.core import arduino; print(arduino.find_arduino_port())"
```

### Verify Logger
```bash
python -c "from src.logging import initialize_logger; initialize_logger('logs'); print('Logger OK')"
```

---

## 🚨 Common Issues

### ❌ ImportError: cannot import name 'config' from 'config'
```
原因: Using old relative imports
解決: Change "from config import config" → "from src.config import config"
```

### ❌ Arduino not found
```
原因: Port not detected or driver missing
解決: 
  1. Check Windows Device Manager
  2. Install Arduino USB driver
  3. Run: python -c "from src.core import arduino; print(arduino.find_arduino_port())"
```

### ❌ Vision Loop too slow (FPS < 30)
```
原因: Detection zone too large or CPU insufficient
解決:
  1. Reduce FOV: config.FOV = 100
  2. Lower MAX_AREA: config.MAX_AREA = 5000
  3. Disable HUMANIZE: config.HUMANIZE = False
```

### ❌ Web Dashboard not accessible
```
原因: Port 5000 already in use
解決:
  1. Check: netstat -an | findstr :5000
  2. Kill: taskkill /PID xxxxx /F
  3. Restart: python main.py
```

---

## 📈 Features by Phase

| Phase | Features | Status |
|-------|----------|--------|
| 1 | Base Vision Detection | ✅ |
| 2 | Arduino Integration | ✅ |
| 3 | Performance Tuning | ✅ |
| 4 | Logging System | ✅ |
| 5 | Web Dashboard | ✅ |
| 6 | Config Profiles | ✅ |
| 7 | RCS Learner | ✅ |
| 8 | Humanize Module | ✅ |
| 9 | Character Learning | ↩️ (Reverted) |
| A1 | System Stabilization | 🟢 Current |

---

## 📚 Developer Documentation

### Adding a New Module

1. **Create Structure**
   ```
   src/mymodule/
   ├─ __init__.py
   ├─ core.py
   └─ helpers.py
   ```

2. **Use Absolute Imports**
   ```python
   # src/mymodule/core.py
   from src.config import config
   from src.core import vision_loop
   from src.logging import data_logger
   ```

3. **Export from __init__.py**
   ```python
   # src/mymodule/__init__.py
   from .core import main_function
   from .helpers import helper_function
   
   __all__ = ['main_function', 'helper_function']
   ```

4. **Use in main.py**
   ```python
   # main.py
   from src.mymodule import main_function
   ```

---

## 🔐 Thread Safety

### Protected Resources
1. **config** - `threading.RLock()`
2. **arduino serial** - `_lock` for writes
3. **detection logger** - `_lock` for appends
4. **vision state** - file-based locking

### Thread Architecture
```
Main Thread (Flask)
├─ Vision Loop Thread (daemon)
│  ├─ Read: config.get_detection_params()
│  ├─ Write: detection logs
│  └─ Call: send_to_arduino()
├─ Arduino Sender Thread (daemon)
│  ├─ Read: movement queue
│  └─ Write: serial port
├─ GC Tuning Thread (daemon)
│  └─ Trigger: gc.collect()
└─ Kill Listener Thread (NOT daemon)
   └─ Wait: END key
```

---

## 📞 Support Resources

| ทรัพยากร | ที่อยู่ |
|---------|--------|
| Quick Start | `QUICK_START.md` |
| Architecture | `SYSTEM_ANALYSIS.md` |
| Tests | `test_imports.py`, `diagnose.py` |
| Logs | `logs/` directory |
| Config | `aimbot_config.json` |

---

## 🎓 Learning Path

1. **Beginner**
   - Read: `QUICK_START.md`
   - Run: `python main.py`
   - Use: Web Dashboard

2. **Intermediate**
   - Read: `SYSTEM_ANALYSIS.md`
   - Understand: Module structure
   - Modify: Configuration

3. **Advanced**
   - Study: Source code
   - Add: New modules
   - Optimize: Performance

---

## ✅ Pre-Launch Checklist

- [ ] Python 3.7+ installed
- [ ] `pip install -r requirements.txt` done
- [ ] Arduino connected & detected
- [ ] `python diagnose.py` → 9/9 checks pass ✅
- [ ] `python main.py` runs without errors
- [ ] Browser can access `http://127.0.0.1:5000/`
- [ ] Color detection working (Dashboard shows target)
- [ ] FPS ≥ 60

---

## 📝 Version Information

- **AIAS Version**: 0.6.0
- **Python**: 3.7+
- **Git HEAD**: `5d0f0bc` (After Phase 9 Rollback)
- **Status**: 🟢 **READY TO RUN**

---

## 📄 License & Credits

- **Project**: AI Aimbot System (AIAS)
- **Architecture**: Modular Python + Flask + Arduino
- **Components**: Vision, Hardware, Logging, Web Interface

---

**Ready to start? → `QUICK_START.md`** 🚀

---

**Last Updated**: 2025-01-XX
**Diagnostic Status**: ✅ All systems operational
