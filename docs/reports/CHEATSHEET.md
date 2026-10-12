# 🚀 AIAS Cheatsheet - Quick Reference

---

## ⚡ Quick Start (30 seconds)

```bash
cd c:\Users\kitatar52\Downloads\aias
python main.py
# → Browser opens at http://127.0.0.1:5000/
```

---

## ⌨️ Control Keys

| Key | Action |
|-----|--------|
| **ALT** | Activate aim |
| **MOUSE1** | Fire |
| **END** | Shutdown |

---

## 🔧 Useful Commands

### Verify System
```bash
python diagnose.py                          # Full system check
python test_imports.py                      # Import verification
```

### Find Arduino
```bash
python -c "from src.core import arduino; print(arduino.find_arduino_port())"
```

### Test Logger
```bash
python -c "from src.logging import initialize_logger; initialize_logger('logs')"
```

### Run with Logging
```bash
python main.py 2>&1 | tee debug.log
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `main.py` | 🚀 Entry point |
| `aimbot_config.json` | ⚙️ Config file |
| `logs/` | 📊 Log directory |
| `src/config/config.py` | 🔧 Config class |
| `src/core/vision.py` | 👁️ Vision loop |
| `src/core/arduino.py` | 🔌 Arduino comm |

---

## ⚙️ Quick Config Changes

### Python Console
```python
from src.config import config

# Read
print(config.FOV)
print(config.LOWER_COLOR)

# Change
config.X_SPEED = 0.5
config.Y_SPEED = 0.45
config.FOV = 150

# Save
config.save("my_profile")

# Load
config.load("my_profile")
```

### Via Web Dashboard
```
http://127.0.0.1:5000/
Settings Tab → Color/Aim → Save
```

### Via JSON File
```
Edit: aimbot_config.json
Restart: python main.py
```

---

## 🎨 HSV Color Values

| Color | Lower | Upper |
|-------|-------|-------|
| Red | [0, 60, 60] | [20, 255, 255] |
| Green | [35, 60, 60] | [90, 255, 255] |
| Blue | [100, 60, 60] | [140, 255, 255] |

---

## 📊 API Endpoints

### Dashboard
```
GET http://127.0.0.1:5000/
```

### Config
```
POST /api/config/save           # Save settings
GET  /api/config/load           # Load settings
GET  /api/config/profiles       # List profiles
POST /api/config/switch         # Change profile
```

### Logger
```
GET  /api/logger/stats          # Get statistics
GET  /api/logger/export         # Export CSV
POST /api/logger/start          # Start logging
POST /api/logger/stop           # Stop logging
```

---

## 🐛 Quick Troubleshooting

### Import Error?
```bash
python test_imports.py
```

### Arduino Not Found?
```bash
python -c "from src.core import arduino; print(arduino.find_arduino_port())"
```

### Slow FPS?
```python
config.FOV = 100        # Reduce detection zone
config.MAX_AREA = 5000  # Limit object size
```

### Web Server Error?
```bash
netstat -an | findstr :5000        # Check port
taskkill /PID xxxxx /F              # Kill process
python main.py                      # Restart
```

### Memory Issues?
```python
config.HUMANIZE = False
config.RCS_ENABLE = False
```

---

## 📈 Performance Tweaks

### Maximum Speed
```python
config.FOV = 100
config.SMOOTH = 2.0
config.HUMANIZE = False
```

### Maximum Accuracy
```python
config.FOV = 200
config.SMOOTH = 15.0
config.HUMANIZE = True
```

### Balanced (Default)
```python
config.FOV = 170
config.SMOOTH = 8.0
config.HUMANIZE = True
```

---

## 🧵 Module Quick Reference

### Config
```python
from src.config import config, initialize_rcs_learner

config.SERIAL_PORT          # "COM3"
config.FOV                  # 170
config.X_SPEED, Y_SPEED     # 0.35, 0.38
config.LOWER_COLOR          # [H, S, V]
config.UPPER_COLOR          # [H, S, V]
config.HUMANIZE             # True/False
config.RCS_ENABLE           # True/False
```

### Vision & Hardware
```python
from src.core import vision_loop, send_to_arduino, find_arduino_port

vision_loop()               # Main loop
send_to_arduino(dx, dy)     # Send movement
find_arduino_port()         # Detect COM port
```

### Logging
```python
from src.logging import initialize_logger, data_logger

initialize_logger("logs")   # Setup
data_logger.log_event(...)  # Log event
data_logger.log_frame(...)  # Log frame
```

### Web
```python
from src.web import app, register_dashboard_route

app.run(port=5000)          # Start server
register_dashboard_route()  # Setup routes
```

---

## 📝 Log Files Location

```
c:\Users\kitatar52\Downloads\aias\logs\
├── session_YYYYMMDD_HHMMSS.json      # Session metadata
├── detections_YYYYMMDD_HHMMSS.csv    # Detection data
└── performance_YYYYMMDD_HHMMSS.csv   # Performance metrics
```

---

## 🎯 Config Profiles

### Create Profile
```python
from src.config import config

config.X_SPEED = 0.5
config.save("custom_profile")
```

### Load Profile
```python
config.load("custom_profile")
```

### List Profiles
```python
profiles = config.list_profiles()
print(profiles)  # ['default', 'custom_profile']
```

### Switch Profile
```python
config.switch_profile("custom_profile")
```

---

## 🔌 Arduino Serial Settings

```
Port: AUTO (COM3 default)
Baud: 115200
Timeout: 0.1s read, 0.1s write
Message Format: "dx,dy\n"
Heartbeat: Every 200ms
```

---

## 🎮 Vision Settings

```
FOV: 170px (Field of View)
MIN_AREA: 5 pixels
MAX_AREA: 20000 pixels
Color Space: HSV (not RGB)
Detection: Contour-based
Tracking: Multi-target capable
```

---

## 📊 Dashboard Features

### System Tab
- Real-time FPS counter
- Target position (x, y)
- Confidence score
- Memory usage
- Session duration

### Settings Tab
- Color HSV sliders
- Aim speed controls
- Smoothing adjustment
- RCS toggle
- Humanize controls

### Logs Tab
- Detection statistics
- Event history
- Performance graphs
- CSV export

---

## 🧪 Health Checks

```bash
# 1. Full diagnostic
python diagnose.py

# 2. Import test
python test_imports.py

# 3. Arduino verify
python -c "from src.core import arduino; print(arduino.find_arduino_port())"

# 4. Config load
python -c "from src.config import config; print(config.FOV)"

# 5. Logger init
python -c "from src.logging import initialize_logger; initialize_logger()"
```

---

## 🚀 Startup Checklist

- [ ] Arduino connected
- [ ] Python 3.7+ installed
- [ ] `pip install -r requirements.txt` done
- [ ] `python diagnose.py` → 9/9 ✅
- [ ] `python test_imports.py` → All imports OK
- [ ] `python main.py` → Runs without errors
- [ ] Browser → http://127.0.0.1:5000/ works

---

## 🎓 Learning Resources

| Document | Topic |
|----------|-------|
| `QUICK_START.md` | Getting started |
| `SYSTEM_ANALYSIS.md` | Technical details |
| `README_TH.md` | Full project info |
| `PROJECT_STATUS.md` | Current status |
| `diagnose.py` | Troubleshooting |

---

## 💡 Pro Tips

1. **Color Picking** - Use web dashboard color picker
2. **Profile Saving** - Save separate profiles for each game
3. **Export Data** - `/api/logger/export` for analysis
4. **Monitor Logs** - Check `logs/` directory for detailed history
5. **Optimize** - Monitor FPS, adjust FOV/MAX_AREA if needed

---

## 🆘 Emergency Restart

If everything breaks:
```bash
# 1. Kill process
taskkill /PID xxxxx /F

# 2. Full diagnostics
python diagnose.py

# 3. Restart
python main.py
```

---

## 📞 Quick Links

- **Config File**: `aimbot_config.json`
- **Logs Folder**: `logs/`
- **Source Code**: `src/`
- **Web Dashboard**: `http://127.0.0.1:5000/`
- **Main Script**: `main.py`

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Verify system | 30 seconds |
| Start system | 5 seconds |
| Access dashboard | 10 seconds |
| Change color | 2 minutes |
| Tune aim speed | 5 minutes |
| Save profile | 1 minute |
| Export logs | 30 seconds |

---

## 🟢 Ready?

```
python main.py
```

**Then visit:**
```
http://127.0.0.1:5000/
```

---

## 📚 Full Documentation

For complete details, see:
- `QUICK_START.md` - Start here!
- `SYSTEM_ANALYSIS.md` - Deep dive
- `README_TH.md` - Full overview

---

**Version**: 0.6.0  
**Status**: ✅ Ready  
**Last Updated**: 2025-01-XX
