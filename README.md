# AIAS — AI Aim System

Color-based aim assist using Arduino HID mouse output, Flask web UI, and Humanize movement.

---

## 📁 Project Structure

```
aias/
├── main.py              ← Entry point (run this)
├── vision.py            ← Screen capture + color detection + aim logic
├── arduino.py           ← Serial HID communication + queue
├── humanize.py          ← Mouse movement humanization (Bezier + Perlin noise)
├── config.py            ← Thread-safe config management + profiles
├── routes.py            ← Flask REST API for web UI
├── requirements.txt     ← Python dependencies
├── aimbot_config.json   ← Saved settings (auto-created)
├── templates/
│   └── index.html       ← Web control panel
└── firmware/
    └── (Arduino .ino firmware files)
```

---

## ⚙️ Requirements

- Python 3.10+
- Windows 10/11
- Arduino Pro Micro (or RP2040 with HID firmware)

---

## 🚀 Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# Optional: faster screen capture
pip install dxcam

# 2. Flash Arduino firmware (see firmware/ folder)

# 3. Run
python main.py
```

Browser opens automatically at **http://127.0.0.1:5000**

API Token is shown in console on first run — enter it in the browser prompt.

---

## 🎮 Usage

| Key | Action |
|-----|--------|
| `SHIFT` (default) | Hold to activate aim |
| `END` | Kill the program |

Settings are configurable from the web UI.

---

## 📦 Arduino Hardware

- **Tested:** Arduino Pro Micro (ATmega32U4)
- **Recommended upgrade:** Waveshare RP2040-Zero or Seeed XIAO RP2040
  - Faster CPU (133MHz vs 16MHz)
  - Custom VID/PID via `boot.py` (no recompile needed)

---

## ⚠️ Notes

- `.api_token` file is auto-generated and **not committed** (see `.gitignore`)
- `aimbot_config.json` contains your personal settings — commit or ignore as preferred
