# 📊 การรวมระบบเก็บข้อมูล (Data Logger Integration)

ระบบเก็บข้อมูลที่ครบครัน สำหรับวิเคราะห์และพัฒนาต่อยอด

---

## 📁 ไฟล์ใหม่

- **`data_logger.py`** - ระบบบันทึก (Logging system)
- **`logger_routes.py`** - API endpoints สำหรับดู/ส่งออกข้อมูล
- **`logs/`** - โฟลเดอร์เก็บข้อมูล (auto-create)

---

## 🔧 วิธีการใช้

### ขั้นตอน 1: เพิ่ม imports ใน `main.py`

```python
from data_logger import initialize_logger
from logger_routes import register_logger_routes
```

### ขั้นตอน 2: เริ่มต้น logger ใน `main.py`

```python
if __name__ == "__main__":
    # ... existing code ...
    
    # Initialize data logger
    logger_instance = initialize_logger(log_dir="logs")
    
    # Register Flask routes
    register_logger_routes(app)
    
    print("[LOGGER] Ready - Visit http://127.0.0.1:5000/api/logger/stats")
```

### ขั้นตอน 3: บันทึกข้อมูลใน `vision.py`

```python
from data_logger import log_detection, log_event, log_frame, log_environment
import cv2
import numpy as np

def vision_loop():
    global fps, latency_start
    
    # ... existing code ...
    
    while True:
        latency_start = time.perf_counter()
        frame = _grab(mon)
        
        # ... detection code ...
        
        # บันทึกข้อมูลประสิทธิภาพ
        latency_ms = (time.perf_counter() - latency_start) * 1000
        log_frame(current_fps, latency_ms)
        
        # บันทึกข้อมูลสภาพแวดล้อม (ทุก 30 เฟรม)
        if frame_count % 30 == 0:
            brightness = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            contrast = np.std(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            
            log_environment(
                frame_count,
                brightness,
                contrast,
                fg_pixels_ratio=mog2_stats.get('fg_pixels_ratio', None),
                target_count=target_count,
                mog2_learning_complete=mog2_stats.get('learning_complete', False)
            )
        
        # บันทึกการตรวจจับ
        if aim_on and target_found:
            log_detection(
                frame_count,
                best_bbox,
                best_confidence,
                detection_type='valid'
            )
        elif outlier_reasons:
            log_detection(
                frame_count,
                curr_bbox,
                0.0,
                detection_type='rejected',
                outlier_reasons=outlier_reasons
            )
        
        # บันทึกเหตุการณ์สำคัญ
        if mog2_learning_complete and not mog2_ready_logged:
            log_event('mog2_ready', 'info', 'MOG2 background model ready')
            mog2_ready_logged = True
        
        if lock_lost > 10:
            log_event('target_lost', 'warning', f'Target lost for {lock_lost} frames')
```

---

## 📊 API Endpoints

### ดู Statistics
```
GET /api/logger/stats
```
**ผลลัพธ์:**
```json
{
  "session_id": "20260114_143022",
  "session_start": "2026-01-14T14:30:22.123456",
  "session_duration_sec": 3645.5,
  "detection": {
    "total": 12543,
    "valid": 11200,
    "rejected": 1343,
    "rejection_rate": "10.7%",
    "avg_confidence": 0.856
  },
  "performance": {
    "current_fps": 144.2,
    "avg_fps": 142.5,
    "min_fps": 85.3,
    "max_fps": 144.8,
    "current_latency_ms": 6.8,
    "avg_latency_ms": 7.2
  }
}
```

### ดึงข้อมูลการตรวจจับ
```
GET /api/logger/detections?limit=50
```

### ดึงการตรวจจับที่ปฏิเสธ
```
GET /api/logger/detections/by-type/rejected?limit=100
```

### ดึงการตรวจจับคะแนนต่ำ
```
GET /api/logger/detections/low-confidence
```

### ดึงเหตุการณ์
```
GET /api/logger/events?limit=50&severity=error
```

### ดึงการสูญเสียเป้าหมาย
```
GET /api/logger/events/target_lost?limit=20
```

### ดึงข้อมูลประสิทธิภาพ
```
GET /api/logger/performance
```

### ดึงข้อมูลสภาพแวดล้อม
```
GET /api/logger/environment?limit=100
```

### ดึงสรุปการตรวจจับ
```
GET /api/logger/detection-summary
```
**ผลลัพธ์:**
```json
{
  "stats": {
    "total": 12543,
    "rejection_rate": "10.7%"
  },
  "outlier_breakdown": {
    "movement_outlier": 420,
    "size_outlier": 380,
    "variance_check_fail": 340,
    "bounds_outlier": 203
  },
  "top_rejection_reasons": [
    ["movement_outlier", 420],
    ["size_outlier", 380],
    ["variance_check_fail", 340]
  ]
}
```

### ดึงสรุปประสิทธิภาพ
```
GET /api/logger/performance-summary
```

### ส่งออก CSV
```
POST /api/logger/export-csv
```
**ผลลัพธ์:** ดาวน์โหลด CSV 2 ไฟล์:
- `detections_20260114_143022.csv`
- `performance_20260114_143022.csv`

### บันทึกข้อมูลด้วยตนเอง
```
POST /api/logger/save
```

---

## 📈 การใช้ข้อมูลสำหรับพัฒนา

### 1. การวิเคราะห์ผลการตรวจจับ

```python
import json
import pandas as pd

# อ่านไฟล์ session
with open('logs/session_20260114_143022.json') as f:
    data = json.load(f)

# ดูเหตุผลการปฏิเสธ
print("Top rejection reasons:")
print(data['detection_stats']['rejection_rate'])

# โหลด CSV
df = pd.read_csv('logs/detections_20260114_143022.csv')
df.groupby('detection_type')['confidence'].agg(['mean', 'std', 'count'])
```

### 2. การตรวจสอบประสิทธิภาพ

```python
import matplotlib.pyplot as plt

# อ่าน performance CSV
perf_df = pd.read_csv('logs/performance_20260114_143022.csv')

# วาด FPS chart
plt.plot(perf_df['fps'])
plt.title('FPS Over Time')
plt.xlabel('Frame')
plt.ylabel('FPS')
plt.show()

# ตรวจหาจุดที่เสถียรภาพต่ำ
low_fps_frames = perf_df[perf_df['fps'] < 30]
print(f"Frames with FPS < 30: {len(low_fps_frames)}")
```

### 3. การสร้าง Dashboard ด้วย Web UI

สามารถเพิ่ม HTML/JS ให้ดู real-time graphs:

```html
<!-- เพิ่มใน templates/index.html -->
<div id="stats-container"></div>

<script>
// ดึงข้อมูลทุก 5 วินาที
setInterval(async () => {
  const res = await fetch('/api/logger/stats');
  const data = await res.json();
  
  document.getElementById('stats-container').innerHTML = `
    <h3>Detection Stats</h3>
    <p>Valid: ${data.detection.valid} (Rejection: ${data.detection.rejection_rate})</p>
    <p>Avg Confidence: ${data.detection.avg_confidence}</p>
    <p>FPS: ${data.performance.current_fps}</p>
  `;
}, 5000);
</script>
```

---

## 🔍 ตัวอย่างการใช้

### ค้นหา Patterns ของการตรวจจับผิด

```python
import json

# โหลดข้อมูล
with open('logs/session_*.json') as f:
    data = json.load(f)

# ค้นหาเมื่อที่ confidence ต่ำ
low_conf_detections = [
    d for d in data['recent_detections']
    if d['confidence'] < 0.5 and d['detection_type'] == 'valid'
]

# ค้นหา pattern ของเหตุผลการปฏิเสธ
rejection_patterns = {}
for event in data['recent_detections']:
    if event['detection_type'] == 'rejected':
        key = tuple(sorted(event['outlier_reasons']))
        rejection_patterns[key] = rejection_patterns.get(key, 0) + 1

# พิมพ์ pattern ที่เด่นที่สุด
for pattern, count in sorted(rejection_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"{pattern}: {count} times")
```

### ตรวจสอบ FPS เมื่อไรต่ำสุด

```python
import pandas as pd

# โหลด performance data
perf_df = pd.read_csv('logs/performance_*.csv')

# ค้นหา FPS ต่ำสุด
min_fps_idx = perf_df['fps'].idxmin()
min_fps_row = perf_df.iloc[min_fps_idx]

print(f"Lowest FPS: {min_fps_row['fps']}")
print(f"Latency at that time: {min_fps_row['latency_ms']}ms")
print(f"Memory at that time: {min_fps_row['memory_mb']}MB")
```

---

## 🎯 ข้อมูลที่เก็บทั้งหมด

### Detection Data
- `frame_number` - เฟรมที่เท่าไหร่
- `bbox` - (x, y, w, h)
- `confidence` - 0-1
- `detection_type` - valid/rejected/predicted
- `outlier_reasons` - เหตุผลการปฏิเสธ

### Performance Data
- `fps` - frames per second
- `latency_ms` - milliseconds
- `memory_mb` - megabytes

### Event Data
- `event_type` - mog2_ready, target_lost, confidence_low, etc.
- `severity` - info, warning, error
- `message` - ข้อความ
- `data` - ข้อมูลเพิ่มเติม

### Environment Data
- `brightness` - 0-255
- `contrast` - 0-255
- `fg_pixels_ratio` - 0-1
- `target_count` - จำนวนเป้าหมาย
- `mog2_learning_complete` - boolean

---

## 💾 ที่เก็บข้อมูล

```
logs/
├── session_20260114_143022.json    # สรุปทั้งเซสชัน
├── detections_20260114_143022.csv  # รายละเอียดการตรวจจับ
└── performance_20260114_143022.csv # ข้อมูลประสิทธิภาพ
```

---

## ⚙️ ตั้งค่า

### auto-save interval
```python
logger_instance = initialize_logger(log_dir="logs")
logger_instance.start_auto_save(interval_seconds=60)  # บันทึกทุก 60 วินาที
```

### max history
```python
from data_logger import DetectionLogger
detector_logger = DetectionLogger(max_history=50000)  # เก็บ 50,000 records
```

---

## 🚀 ข้อมูลพร้อมใช้ทันที

ตอนนี้:
- ✅ `data_logger.py` สร้างแล้ว
- ✅ `logger_routes.py` สร้างแล้ว
- ✅ 15+ API endpoints พร้อมใช้

**เพียงแค่:**
1. เพิ่ม imports ใน main.py
2. เรียก `initialize_logger()`
3. เรียก `register_logger_routes(app)`
4. เพิ่มการเรียก log_* functions ใน vision.py

ข้อมูลก็จะเริ่มเก็บ!
