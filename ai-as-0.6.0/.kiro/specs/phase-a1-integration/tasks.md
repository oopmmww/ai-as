# Tasks: Phase A1 Integration

## Task 1: Integrate Logger Routes into main.py
**Status**: not_started
**Priority**: 1
**Dependencies**: none

### Subtasks
- [x] Add import statements for logger modules (data_logger, logger_routes)
- [x] Call initialize_logger(log_dir="logs") before app.run()
- [ ] Call register_logger_routes(app) to register API endpoints
- [ ] Verify no import or initialization errors

### Description
แก้ไข main.py เพื่อรวมระบบ logger routes เข้าไป โดยตั้งค่า logger และลงทะเบียน API endpoints ให้พร้อมใช้งาน

---

## Task 2: Integrate Dashboard Route into main.py
**Status**: not_started
**Priority**: 2
**Dependencies**: [Task 1]

### Subtasks
- [ ] Add import statement for dashboard_route module
- [ ] Call register_dashboard_route(app) before app.run()
- [ ] Change root path "/" to redirect/point to dashboard
- [ ] Verify dashboard is accessible at http://127.0.0.1:5000/dashboard

### Description
แก้ไข main.py เพื่อรวม dashboard route เข้าไป และตั้งค่าให้ dashboard เป็นหน้าแรก

---

## Task 3: Update Cleanup Handler for Logger
**Status**: not_started
**Priority**: 3
**Dependencies**: [Task 1]

### Subtasks
- [ ] Add logger_instance.stop_and_save() call in _cleanup() function
- [ ] Verify logger data is saved to JSON file on shutdown
- [ ] Test cleanup process without errors

### Description
แก้ไข _cleanup() function ใน main.py เพื่อให้ข้อมูล logger ถูกบันทึกลงไฟล์เมื่อแอปปิด

---

## Task 4: Verify All Systems Initialize Without Errors
**Status**: not_started
**Priority**: 4
**Dependencies**: [Task 1, Task 2, Task 3]

### Subtasks
- [ ] Start main.py and check for import errors
- [ ] Check for initialization errors
- [ ] Verify logger is ready on app startup
- [ ] Verify dashboard is accessible via browser
- [ ] Verify API endpoints are responding

### Description
ทดสอบให้แน่ใจว่าระบบทั้งหมดเริ่มต้นได้สำเร็จโดยไม่มี error

---

## Task 5: Add Logging Calls to vision.py
**Status**: not_started
**Priority**: 5
**Dependencies**: [Task 1]

### Subtasks
- [ ] Add import statements for logging functions from data_logger
- [ ] Add log_frame(fps, latency_ms) call after each frame processing
- [ ] Add log_detection(...) for valid and rejected detections
- [ ] Add log_environment(...) every 60 frames
- [ ] Add log_event(...) for critical events (mog2_ready, target_lost, etc.)

### Description
แก้ไข vision.py เพื่อเพิ่มการเรียกฟังก์ชัน logging อัตโนมัติขณะประมวลผลภาพ

---

## Task 6: Verify Logging Data is Collected Correctly
**Status**: not_started
**Priority**: 6
**Dependencies**: [Task 5]

### Subtasks
- [ ] Run vision.py with logging enabled
- [ ] Verify log_frame calls are working
- [ ] Verify log_detection calls are working
- [ ] Verify log_environment calls are working
- [ ] Verify log_event calls are working
- [ ] Check logger output files for data

### Description
ทดสอบให้แน่ใจว่าข้อมูล logging ถูกเก็บบันทึกได้ถูกต้องจากทุกจุดใน vision.py

