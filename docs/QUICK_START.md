# 🚀 AIAS Quick Start Guide

**ภาษาไทย** | [English](#english-version)

---

## 📋 สิ่งที่ต้องเตรียม

### 1. ตรวจสอบที่ตั้งโปรเจ็กต์
```bash
cd c:\Users\kitatar52\Downloads\aias
```

### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

หรือติดตั้งเพิ่มเติม:
```bash
pip install noise          # สำหรับ Perlin noise
```

### 3. ตรวจสอบ Arduino
- เสียบสาย USB-Serial ของ Arduino
- Windows ควรตรวจจับเป็น `COM3` หรือ `COM4`
- ตรวจสอบด้วย:
```bash
python -c "from src.core import arduino; print(arduino.find_arduino_port())"
```

---

## 🎮 การใช้งาน

### วิธีที่ 1: เริ่มต้นระบบแบบปกติ

```bash
python main.py
```

**สิ่งที่เกิดขึ้น:**
1. ✅ ตรวจสอบ hardware (camera, Arduino)
2. ✅ เชื่อมต่อกับ Arduino
3. ✅ เริ่มต้น Vision Loop (ตรวจจับเป้าหมาย)
4. ✅ เปิด Browser ไปที่ `http://127.0.0.1:5000/`
5. 🎯 พร้อมใช้งาน!

**ปุ่มควบคุม:**
- **ALT** - ยืนยัน (Activate aim)
- **MOUSE1** - ยิง (Trigger fire)
- **END** - ปิดโปรแกรม

---

### วิธีที่ 2: ทดสอบ Import เท่านั้น

```bash
python test_imports.py
```

**ผลลัพธ์:**
```
============================================================
[TEST] Verifying all imports...
============================================================

[1] Testing src.config...
    ✅ config imported

[2] Testing src.core...
    ✅ arduino, vision_loop imported

[3] Testing src.logging...
    ✅ logging modules imported

[4] Testing src.web...
    ✅ Flask app imported

[5] Testing data_logger convenience functions...
    ✅ log_event() works

============================================================
[SUCCESS] All imports verified! ✅
============================================================
```

---

### วิธีที่ 3: ทดสอบ Arduino Connection

```bash
python -c "from src.core import arduino; port = arduino.find_arduino_port(); print(f'Arduino at {port}')"
```

---

## 🌐 Web Dashboard

### เข้าหน้าบ้าน
```
http://127.0.0.1:5000/
```

### ฟีเจอร์ที่ใช้ได้

#### 1. 📊 Dashboard Tab
- ดูสถานะระบบ (CPU, Memory)
- ดู FPS ของ Vision Loop
- ดูตำแหน่งเป้าหมาย (x, y)
- ดูระดับ Confidence

#### 2. ⚙️ Settings Tab
- **Color Detection**
  - HSV Range: Lower/Upper bounds
  - Sliders สำหรับปรับ
- **Aim Settings**
  - X Speed (0.1 - 2.0)
  - Y Speed (0.1 - 2.0)
  - Smooth Factor (1 - 20)
  - Offset X/Y
- **RCS (Recoil Compensation)**
  - Enable/Disable
  - RCS Strength
- **Humanize Settings**
  - Enable/Disable
  - Noise Strength (0.1 - 1.0)

#### 3. 📈 Logs Tab
- ดูสถิติการตรวจจับ
- ดูประวัติ Events
- Export CSV

---

## 📁 โครงสร้างไฟล์

```
c:\Users\kitatar52\Downloads\aias\
├── main.py                    # 🚀 Entry point
├── test_imports.py            # ✅ Import testing
├── requirements.txt           # 📦 Dependencies
│
├── src/
│   ├── config/                # ⚙️ Configuration
│   │   ├── config.py          # Config class
│   │   └── rcs_learner.py    # RCS learning
│   │
│   ├── core/                  # 🎯 Core vision & hardware
│   │   ├── vision.py          # Vision processing
│   │   ├── arduino.py         # Arduino communication
│   │   └── humanize.py        # Movement smoothing
│   │
│   ├── logging/               # 📝 Data logging
│   │   ├── data_logger.py     # Session logging
│   │   └── event_logger.py    # Event tracking
│   │
│   └── web/                   # 🌐 Web dashboard
│       └── routes.py          # Flask API endpoints
│
├── templates/
│   ├── index.html             # Main dashboard
│   ├── dashboard.html         # System status
│   └── settings.html          # Configuration UI
│
├── logs/                      # 📊 Log files
│   ├── session_*.json         # Session records
│   ├── detections_*.csv       # Detection data
│   └── performance_*.csv      # Performance metrics
│
├── config/
│   └── aimbot_config.json     # Saved profiles
│
└── docs/
    ├── SYSTEM_ANALYSIS.md     # 📋 Full analysis
    └── QUICK_START.md         # 🚀 This file
```

---

## 🔧 Configuration

### โปรไฟล์ Config

**ที่ตั้ง**: `c:\Users\kitatar52\Downloads\aias\aimbot_config.json`

**ตัวอย่าง:**
```json
{
  "default": {
    "SERIAL_PORT": "COM3",
    "SERIAL_BAUD": 115200,
    "FOV": 170,
    "X_SPEED": 0.35,
    "Y_SPEED": 0.38,
    "LOWER_COLOR": [130, 60, 70],
    "UPPER_COLOR": [175, 255, 255],
    "HUMANIZE": true,
    "HUMAN_STR": 0.5
  },
  "custom_profile": {
    "X_SPEED": 0.5,
    "...": "..."
  }
}
```

### การเปลี่ยน Config ระหว่างรัน

**ผ่าน Web Dashboard:**
1. ไปที่ Settings Tab
2. ปรับค่าต่าง ๆ
3. กดปุ่ม Save
4. Auto-apply

**ผ่าน Python:**
```python
from src.config import config

# อ่านค่า
print(config.SERIAL_PORT)
print(config.FOV)
print(config.LOWER_COLOR)

# เปลี่ยนค่า (thread-safe)
config.X_SPEED = 0.5
config.Y_SPEED = 0.45
config.LOWER_COLOR = [130, 60, 70]

# บันทึก Profile
config.save("my_profile")

# โหลด Profile
config.load("my_profile")

# เปลี่ยน Profile
config.switch_profile("my_profile")

# ดูโปรไฟล์ทั้งหมด
profiles = config.list_profiles()
```

---

## 📊 Logging & Data Export

### Log Files Location
```
logs/
├── session_20250101_143304.json      # Session metadata
├── detections_20250101_143304.csv    # Detection data
└── performance_20250101_143304.csv   # Performance metrics
```

### ดูข้อมูล Log ผ่าน API

**Get Session Stats:**
```bash
curl http://127.0.0.1:5000/api/logger/stats
```

**Response:**
```json
{
  "session_id": "SES_20250101_143304",
  "start_time": "2025-01-01T14:33:04",
  "duration_seconds": 600,
  "total_frames": 60000,
  "total_detections": 450,
  "average_fps": 100,
  "average_latency_ms": 8.5,
  "detection_stats": {
    "valid": 430,
    "rejected": 20,
    "predicted": 50,
    "rejection_rate": "4.4%",
    "avg_confidence": 0.87
  }
}
```

**Export to CSV:**
```bash
curl http://127.0.0.1:5000/api/logger/export -o exported_data.zip
```

---

## 🐛 Troubleshooting

### ❌ Error: `ImportError: cannot import name 'config' from 'config'`

**สาเหตุ**: Import ใช้ path ที่ไม่ถูกต้อง

**วิธีแก้**:
```bash
# ตรวจสอบว่า config.py อยู่ใน src/config/ ไม่ใช่ root
ls src/config/config.py

# ควร output: src/config/config.py
```

---

### ❌ Error: `ModuleNotFoundError: No module named 'src'`

**สาเหตุ**: Run จากไดเรกทอรีที่ผิด

**วิธีแก้**:
```bash
# ✅ CORRECT
cd c:\Users\kitatar52\Downloads\aias
python main.py

# ❌ WRONG
cd c:\Users\kitatar52\Downloads\aias\src
python main.py
```

---

### ❌ Arduino not found / Connection failed

**สาเหตุ**: Arduino ไม่ได้เสียบ หรือ Driver ไม่ติดตั้ง

**วิธีแก้**:
```bash
# 1. ตรวจสอบว่า Arduino ติดอยู่ด้วย
# Windows Device Manager → COM & LPT Ports

# 2. ตรวจสอบ Port
python -c "from src.core import arduino; print(arduino.find_arduino_port())"

# 3. ถ้าไม่เจอ ลองติดตั้ง Driver
# https://www.arduino.cc/en/Guide/Windows
```

---

### ❌ Vision Loop too slow (FPS < 30)

**สาเหตุ**: PC ต่ำ หรือ Detection parameters ยากเกินไป

**วิธีแก้**:
```bash
# 1. ลด FOV (Field of View)
config.FOV = 100  # ลดจาก 170 เป็น 100

# 2. ลด MAX_AREA
config.MAX_AREA = 5000  # ลดจาก 20000 เป็น 5000

# 3. Disable RCS learning
config.RCS_ENABLE = False

# 4. Disable Humanize
config.HUMANIZE = False
```

---

### ❌ Web Dashboard not accessible

**สาเหตุ**: Port 5000 ถูกใช้โดยแอปอื่น

**วิธีแก้**:
```bash
# 1. ตรวจสอบ Port
netstat -an | findstr :5000

# 2. หา PID ที่ใช้ Port
tasklist | findstr "(PID)"

# 3. Kill process
taskkill /PID xxxxx /F

# 4. Restart main.py
python main.py
```

---

## 💡 Pro Tips

### 1. ใช้ Color Picker เพื่อตั้งค่าสี
- ไปที่ Settings → Color Detection
- ใช้ Color Picker Tool
- Select พื้นที่ที่เป็นเป้าหมาย
- Auto-adjust HSV ranges

### 2. ทดสอบ Detection ก่อนใช้งาน
```bash
# ใน Dashboard
Settings → Color Detection → Test Mode
```

### 3. บันทึก Multiple Profiles
```python
# Create profile สำหรับแต่ละ game/setting
config.switch_profile("default")
config.X_SPEED = 0.35
config.save("default")

config.switch_profile("valorant")
config.X_SPEED = 0.45
config.LOWER_COLOR = [120, 50, 80]
config.save("valorant")
```

### 4. Monitor Performance
```bash
# ใน Dashboard → Logs Tab
# ดู Average FPS, Latency
# ดู Detection Success Rate
```

### 5. Export & Analyze Data
```bash
# Export logs
curl http://127.0.0.1:5000/api/logger/export -o data.zip

# Analyze ด้วย Python
import json
import pandas as pd

# Load detections
detections = pd.read_csv('detections_*.csv')
print(detections.describe())
```

---

## 🎯 Next Steps

### หลังจากเริ่มต้นสำเร็จ

1. **ปรับ Color Detection**
   - ไปที่ Settings
   - ใช้ Color Picker
   - ตั้งค่า HSV ranges ให้แม่นยำ

2. **ทดสอบ Aim Speed**
   - เริ่มด้วย default (0.35, 0.38)
   - ปรับขึ้นช้า ๆ
   - หา sweet spot สำหรับระบบของคุณ

3. **Enable Humanize**
   - ลดความสงสัยจาก anti-cheat
   - ปรับ noise strength

4. **Setup RCS Learning**
   - Enable RCS
   - ยิงหลายครั้ง
   - System จะเรียนรู้ recoil pattern

5. **Monitor Logs**
   - ตรวจสอบ success rate
   - ดู average latency
   - ดู memory usage

---

## 📞 Support

### ดูเพิ่มเติม
- `SYSTEM_ANALYSIS.md` - บริบทระบบแบบลึก
- `requirements.txt` - Dependencies ทั้งหมด
- Logs directory - ข้อมูล session & detections

### Debug Mode
```bash
# Print verbose logs
python main.py  2>&1 | tee debug.log

# Check specific module
python -c "from src.core import vision; print(vision.__file__)"
```

---

## ✅ Checklist ก่อนใช้งาน

- [ ] Python 3.7+ ติดตั้งแล้ว
- [ ] `pip install -r requirements.txt` เรียบร้อย
- [ ] Arduino เสียบแล้ว
- [ ] `python test_imports.py` ผ่าน ✅
- [ ] `python main.py` รัน ✅
- [ ] Browser เข้า `http://127.0.0.1:5000/` ได้
- [ ] Color Detection ทำงาน (ดู Dashboard)
- [ ] FPS ≥ 60

---

**หากมีปัญหา** ให้ check `SYSTEM_ANALYSIS.md` สำหรับรายละเอียดลึกเพิ่มเติม 📋

---

# English Version

## 🚀 Quick Start

### 1. Prerequisites
```bash
cd c:\Users\kitatar52\Downloads\aias
pip install -r requirements.txt
```

### 2. Run System
```bash
python main.py
```

### 3. Access Dashboard
```
http://127.0.0.1:5000/
```

### 4. Control Keys
- **ALT** - Activate aim
- **MOUSE1** - Fire
- **END** - Shutdown

---

**For more details, see `SYSTEM_ANALYSIS.md`** 📋
