# 📊 Dashboard Setup Guide

ระบบ Dashboard สำหรับดูข้อมูลแบบ real-time พร้อมกราฟ

---

## 🚀 ติดตั้งด่วน

### Step 1: เพิ่ม imports ใน `main.py`

```python
from data_logger import initialize_logger
from logger_routes import register_logger_routes
from dashboard_route import register_dashboard_route
```

### Step 2: เริ่มต้น logger ใน main.py (ก่อน app.run)

```python
if __name__ == "__main__":
    # ... existing code ...
    
    # ✅ เพิ่มเหล่านี้
    logger_instance = initialize_logger(log_dir="logs")
    register_logger_routes(app)
    register_dashboard_route(app)
    
    print("[LOGGER] Dashboard ready at http://127.0.0.1:5000/dashboard")
    
    try:
        app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger_instance.stop_and_save()
```

### Step 3: บันทึกข้อมูลใน `vision.py`

```python
# เพิ่มที่ top
from data_logger import log_detection, log_event, log_frame, log_environment
import numpy as np
import cv2

# ใน vision_loop()
def vision_loop():
    frame_count = 0
    last_fps = 0
    
    while True:
        t_start = time.perf_counter()
        frame = _grab(mon)
        
        if frame is None:
            continue
        
        # ... existing detection code ...
        
        # ✅ บันทึกประสิทธิภาพ
        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000
        current_fps = 1.0 / (t_end - t_start) if (t_end - t_start) > 0 else 0
        log_frame(current_fps, latency_ms)
        
        # ✅ บันทึกข้อมูลสภาพแวดล้อม (ทุก 60 เฟรม)
        if frame_count % 60 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            log_environment(
                frame_count,
                brightness,
                contrast,
                fg_pixels_ratio=mog2_stats.get('fg_pixels_ratio', None),
                target_count=target_count,
                mog2_learning_complete=mog2_stats.get('learning_complete', False)
            )
        
        # ✅ บันทึกการตรวจจับ (valid)
        if aim_on and target_found:
            log_detection(
                frame_count,
                best_bbox,
                best_confidence,
                detection_type='valid'
            )
        
        # ✅ บันทึกการตรวจจับ (rejected)
        elif outlier_reasons:
            log_detection(
                frame_count,
                (x, y, w, h),
                0.0,
                detection_type='rejected',
                outlier_reasons=outlier_reasons
            )
        
        # ✅ บันทึกเหตุการณ์สำคัญ
        if mog2_learning_complete and not mog2_event_logged:
            log_event('mog2_ready', 'info', 'MOG2 model ready for detection')
            mog2_event_logged = True
        
        if lock_lost > 20:
            log_event('target_lost', 'warning', f'Target lost for {lock_lost} frames')
        
        frame_count += 1
```

---

## 🌐 ใช้งาน Dashboard

### เข้าถึง
```
http://127.0.0.1:5000/dashboard
```

### ฟีเจอร์

**📈 Real-time Graphs**
- FPS History - ดูประสิทธิภาพตามเวลา
- Latency History - ความล่าช้าของ vision loop
- Memory Usage - การใช้ RAM
- Detection Breakdown - Pie chart ของการตรวจจับ (valid/rejected/predicted)

**📊 Statistics Cards**
- Detection Stats: Total, Valid, Rejected, Rejection Rate, Avg Confidence
- Performance: Current FPS, Avg FPS, Min FPS, Latency
- System Health: Memory, Peak Memory, Health Status, Low FPS Frames

**❌ Rejection Breakdown**
- Top 5 reasons ที่ปฏิเสธการตรวจจับ
- แสดงเป็น Bar chart ที่สำหรับเปรียบเทียบ

**📋 Recent Events**
- ล่าสุด 20 events
- Color-coded: info (green), warning (orange), error (red)
- เหตุการณ์อย่าง: mog2_ready, target_lost, confidence_low

---

## 🎯 ใช้ Dashboard เพื่อวิเคราะห์

### 1. ตรวจสอบประสิทธิภาพ
```
ดูกราฟ FPS + Latency:
- FPS ตกต่ำ < 30 fps? → ปัญหา CPU
- Latency สูง > 30ms? → ปัญหา detection logic
- Memory เพิ่มขึ้นเรื่อย? → memory leak
```

### 2. ตรวจสอบคุณภาพตรวจจับ
```
ดู Detection Breakdown + Rejection Reasons:
- Rejection rate สูง > 20%? → ปรับ validators
- movement_outlier บ่อย? → ปรับ max_speed_pct
- size_outlier บ่อย? → ปรับ min/max_size_ratio
```

### 3. ตรวจสอบเหตุการณ์
```
ดู Recent Events:
- target_lost บ่อย? → ปัญหา tracking
- confidence_low เยอะ? → ปรับ confidence threshold
- mog2_ready ไม่ขึ้น? → MOG2 ยังเรียนรู้
```

---

## 💾 ส่งออกข้อมูล

### ปุ่ม "Save Session"
```
บันทึกข้อมูล session ลง JSON
→ logs/session_20260114_143022.json
```

### ปุ่ม "Export CSV"
```
ส่งออก 2 ไฟล์ CSV:
→ logs/detections_20260114_143022.csv
→ logs/performance_20260114_143022.csv
```

---

## 📱 Refresh Behavior

- **Auto-refresh**: ทุก 5 วินาที (อัตโนมัติ)
- **Manual refresh**: Click "Refresh Now" button

---

## 🔧 Troubleshooting

### Dashboard ไม่แสดง
```
1. ตรวจสอบ imports ใน main.py
2. ตรวจสอบ register_dashboard_route(app) เรียกแล้ว
3. ตรวจสอบ templates/dashboard.html มีอยู่
```

### ข้อมูลไม่ปรากฏ
```
1. ตรวจสอบ log_frame, log_detection เรียกจาก vision.py
2. ตรวจสอบ initialize_logger() เรียกแล้ว
3. ตรวจสอบ console ไม่มี error
```

### Graphs ว่าง ๆ
```
1. รอบ 5-10 วินาที (ต้องเก็บข้อมูลพอตั้ง)
2. Refresh page
3. ตรวจสอบ network console (F12) ดู API errors
```

---

## 🎨 Customization

### เปลี่ยนสี

เปิด `templates/dashboard.html` ค้นหา:
```css
--primary-color: #00d9ff;
--danger-color: #f44336;
--warning-color: #ff9800;
--success-color: #4caf50;
```

### เปลี่ยน refresh interval

ในไฟล์ `dashboard.html` หา:
```javascript
setInterval(refreshData, 5000);  // เปลี่ยน 5000 → milliseconds
```

### เพิ่มกราฟใหม่

```javascript
// ใน initCharts()
newChart = new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [...] },
    options: { ... }
});

// ใน updateCharts()
newChart.data.datasets[0].data = newData;
newChart.update();
```

---

## 📊 Data Flow

```
vision.py
  ↓
log_detection() / log_frame() / log_environment()
  ↓
data_logger.py (DetectionLogger, PerformanceLogger, etc.)
  ↓
Auto-save JSON ทุก 60 วินาที
  ↓
logger_routes.py (/api/logger/*)
  ↓
dashboard.html (fetch + display)
```

---

## ✅ ตรวจสอบว่าพร้อม

```python
# ใน main.py ควรมี:
1. ✅ from data_logger import initialize_logger
2. ✅ from logger_routes import register_logger_routes
3. ✅ from dashboard_route import register_dashboard_route
4. ✅ logger_instance = initialize_logger()
5. ✅ register_logger_routes(app)
6. ✅ register_dashboard_route(app)

# ใน vision.py ควรมี:
1. ✅ from data_logger import log_*
2. ✅ log_frame(fps, latency_ms)
3. ✅ log_detection(...)
4. ✅ log_environment(...)
5. ✅ log_event(...)
```

---

## 🚀 Quick Start

```bash
# 1. เพิ่มไฟล์ 3 ตัวใหม่ (มีแล้ว):
#    - data_logger.py
#    - logger_routes.py
#    - dashboard_route.py
#    - templates/dashboard.html

# 2. แก้ main.py (เพิ่ม 3 บรรทัด)

# 3. แก้ vision.py (เพิ่มการเรียก log_*)

# 4. รัน
python main.py

# 5. เปิด
http://127.0.0.1:5000/dashboard
```

Done! 🎉
