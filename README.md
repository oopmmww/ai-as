# AIAS — AI Aim System

Advanced color-based aim assist with Arduino HID output, multi-target tracking, adaptive color detection, and complete logging system.

**Status:** Phase 8 ✅ | Project Restructured | Active Development

**Latest Update:** โครงสร้างโปรเจ็กต์ปรับปรุง - src/ modules สำหรับ maintainability

---

## 🎯 Features

### Core Functionality
- **Color Detection:** HSV-based detection with adaptive thresholds
- **Multi-Target Tracking:** Track up to 5 targets simultaneously with velocity prediction
- **Arduino HID Output:** Direct USB mouse control via Arduino Pro Micro
- **Humanized Movement:** Bezier curves + Perlin noise to avoid detection
- **Recoil Control System:** Smart RCS with learned weapon patterns

### Advanced Features
- **Adaptive Color Detection:** Adjusts HSV thresholds based on frame brightness
- **Spike Detection:** Monitors FPS drops and latency spikes
- **Confidence Smoothing:** EMA smoothing to reduce jitter
- **Garbage Collection Tuning:** Manual GC control for stable performance
- **Multi-profile Support:** Save/load different configurations

### Monitoring & Logging
- **Real-time Dashboard:** Live stats, performance charts, rejection breakdown
- **Data Logging:** Automatic recording of detections, performance, events
- **Session Export:** JSON + CSV export for analysis
- **Settings Panel:** Toggle logging, view config, access dashboard

---

## 📁 Project Structure (Phase 8 - Reorganized)

```
aias/
├── main.py                      ← Entry point (run this)
├── requirements.txt             ← Python dependencies
├── src/                         ← Main source code (Phase 8 - NEW)
│   ├── __init__.py
│   ├── core/                    ← Core vision & hardware modules
│   │   ├── __init__.py
│   │   ├── vision.py            ← Vision loop, detection, multi-target tracking
│   │   ├── arduino.py           ← Serial HID communication
│   │   └── humanize.py          ← Movement humanization
│   ├── config/                  ← Configuration & settings
│   │   ├── __init__.py
│   │   ├── config.py            ← Thread-safe config + profile management
│   │   └── rcs_learner.py       ← Smart RCS pattern learning
│   ├── logging/                 ← Data logging system
│   │   ├── __init__.py
│   │   ├── data_logger.py       ← Logging (detection, performance, events)
│   │   └── logger_routes.py     ← Logger API endpoints
│   └── web/                     ← Flask web interface
│       ├── __init__.py
│       ├── routes.py            ← REST API endpoints
│       └── dashboard_route.py   ← Dashboard UI routes
├── templates/                   ← HTML templates
│   ├── index.html               ← Main control panel
│   ├── dashboard.html           ← Analytics dashboard
│   └── settings.html            ← Settings page (standalone)
├── docs/                        ← Documentation (Phase 8 - NEW)
│   ├── CHANGELOG.md             ← Development history (Phase 1-8)
│   ├── DASHBOARD_SETUP.md       ← Dashboard guide
│   ├── DEVELOPMENT_ROADMAP.md   ← Future plans
│   ├── INTEGRATION_SUMMARY.md   ← System architecture
│   ├── LOGGER_INTEGRATION.md    ← Logging details
│   └── PLAN_A_DETAILED.md       ← Detailed plans
├── config/                      ← Configuration files (Phase 8 - NEW)
│   └── aimbot_config.json       ← Saved settings (auto-created)
├── firmware/
│   └── firmware.ino             ← Arduino sketch
├── logs/                        ← Session logs (auto-created)
│   ├── session_*.json           ← Session data
│   ├── detections_*.csv         ← Detection logs
│   └── performance_*.csv        ← Performance metrics
├── .github/
│   ├── workflows/lint.yml       ← GitHub Actions
│   └── ISSUE_TEMPLATE/          ← Issue templates
├── .kiro/
│   └── specs/phase-a1-integration/
│       ├── requirements.md      ← Integration requirements
│       ├── design.md            ← Technical design
│       └── tasks.md             ← Task checklist
├── CONTRIBUTING.md              ← Contributor guide
├── LICENSE                      ← MIT License
└── README.md                    ← This file
```

**Key Changes (Phase 8):**
- ✅ Modularized `src/` package structure
- ✅ Moved docs to `docs/` folder
- ✅ Moved configs to `config/` folder
- ✅ Cleaner imports: `from src.core import vision_loop`
- ✅ Better separation of concerns (core, config, logging, web)

---

## ⚙️ Requirements

- **Python:** 3.10+
- **OS:** Windows 10/11
- **Hardware:** Arduino Pro Micro (or RP2040 with HID firmware)
- **Dependencies:** See `requirements.txt`

---

## 🚀 Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. (Optional) Install faster screen capture
pip install dxcam

# 3. Flash Arduino firmware (see firmware/ folder)
# - Use Arduino IDE to upload firmware.ino to your microcontroller

# 4. Run the application
python main.py
```

The browser automatically opens at **http://127.0.0.1:5000**

First run prompts for API Token (printed in console)

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `ALT` (default) | Activate aim assist |
| `END` | Graceful shutdown |
| `Right-click (Vision)` | Pick color from screen |

---

## 🌐 Web Interface

### Main Panel (`/`)
- **Aim:** Zone selection, smoothing, speed controls
- **Detection:** FOV, area filters, offset tuning
- **Keys:** Keybinding customization
- **RCS:** Recoil control strength
- **Display:** Vision window toggles
- **Color:** Enemy color presets
- **Profile:** Save/load configurations
- **Settings:** Logging toggle, dashboard link, config display

### Dashboard (`/dashboard`)
- Real-time statistics (FPS, detections, target lock)
- Performance charts (FPS trend, latency)
- Rejection breakdown (shape, movement, size, confidence)
- Trigger statistics
- System health status

### Settings (`/settings`)
- Toggle data logging on/off
- Quick link to dashboard
- View current configuration (JSON)

---

## 📊 Data Logging

Automatic logging when enabled (configurable):

- **Detections:** Valid/rejected with confidence, bbox, outlier reasons
- **Performance:** FPS, latency, frame timing
- **Events:** Trigger fires, target lost, Arduino errors
- **Environment:** Brightness, contrast, foreground ratio

Auto-save on shutdown: `logs/session_YYYYMMDD_HHMMSS.json` + CSV exports

---

## 🔧 Arduino Hardware

### Tested Microcontrollers
- ✅ Arduino Pro Micro (ATmega32U4) — baseline, works but slower
- ✅ Waveshare RP2040-Zero — recommended (faster, same price)
- ✅ Seeed XIAO RP2040 — excellent choice

### Firmware Setup
1. Download Arduino IDE
2. Install board support (RP2040 or ATmega32U4)
3. Upload `firmware/firmware.ino` to microcontroller
4. Update `config.SERIAL_PORT` in config.py if needed

---

## 📝 Development Phases

See **[docs/CHANGELOG.md](docs/CHANGELOG.md)** for detailed history:

- **Phase 1:** Arduino COM port connection fix
- **Phase 2:** Dashboard + analytics UI
- **Phase 3:** Complete logging system integration
- **Phase 4:** Advanced features (multi-target, adaptive color, smart RCS)
- **Phase 5:** Performance tuning (GC optimization, spike detection)
- **Phase 6:** Outlier threshold relaxation
- **Phase 7:** Settings panel + logging control
- **Phase 8:** Project restructuring - src/ modules for maintainability ← **Current**

---

## ⚠️ Important Notes

- `.api_token` is auto-generated and **NOT committed** (security, see `.gitignore`)
- `aimbot_config.json` contains personal settings — decide whether to commit
- `rcs_patterns.json` stores learned weapon patterns
- `logs/` directory is excluded from Git (auto-created)
- All timestamps in logs are in UTC

---

## 🔐 Security

- API Token generated on first run (random 32-char hex)
- Token required for all `/api/` endpoints
- No credentials stored in source code
- Serial communication is local-only (no network)

---

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** — Feature history and roadmap
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** — System architecture
- **[DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)** — Future plans

---

## 🤝 Contributing

This is a personal project, but pull requests are welcome for:
- Bug fixes
- Performance improvements
- Hardware compatibility
- Documentation

---

## ⚖️ License

Proprietary — AIAS Detection System
