# Phase A1: Integrate Logging System and Dashboard

## บทนำ

โครงการ AIAS Detection System ต้องการรวมระบบ data logging และ dashboard เข้ากับส่วนหลักของแอปพลิเคชัน เพื่อให้สามารถติดตามผลการทำงาน ประสิทธิภาพ และเหตุการณ์ต่างๆ ในเวลาจริงได้

## ความต้องการของผู้ใช้

### Requirement 1: Integrate Logger Routes into main.py

**User Story:** ในฐานะผู้ดูแลระบบ ฉันต้องการให้ระบบ logging API endpoints พร้อมใช้งาน เพื่อให้สามารถค้นหาและวิเคราะห์ข้อมูลการทำงาน

#### Acceptance Criteria

1. main.py ต้อง import โมดูล `data_logger` และ `logger_routes`
2. ต้องเรียก `initialize_logger(log_dir="logs")` ก่อน `app.run()`
3. ต้องเรียก `register_logger_routes(app)` เพื่อลงทะเบียน API endpoints ใน Flask app
4. ไม่ควรมี error ที่ทำให้ app crash ตอนเริ่มต้น

### Requirement 2: Integrate Dashboard Route into main.py

**User Story:** ในฐานะผู้ใช้ ฉันต้องการให้ dashboard UI พร้อมใช้งานที่ `/dashboard` เพื่อดูข้อมูลแบบเรียลไทม์

#### Acceptance Criteria

1. main.py ต้อง import `dashboard_route` module
2. ต้องเรียก `register_dashboard_route(app)` ก่อน `app.run()`
3. Dashboard ต้องสามารถเข้าถึงได้ที่ `http://127.0.0.1:5000/dashboard`
4. Root path `/` ต้องเปลี่ยนไปชี้ไปที่ dashboard แทนหน้า index เดิม

### Requirement 3: Update Cleanup Handler for Logger

**User Story:** ในฐานะผู้ดูแลระบบ ฉันต้องการให้ข้อมูล logging ถูกบันทึกลงไฟล์ เมื่อแอปพลิเคชันปิด เพื่อไม่ให้สูญหายข้อมูลที่บันทึกไว้

#### Acceptance Criteria

1. ฟังก์ชัน `_cleanup()` ต้องเรียก `logger_instance.stop_and_save()`
2. ข้อมูล logging ต้องถูกบันทึกไปยังไฟล์ JSON ก่อนปิดแอปพลิเคชัน
3. ไม่ควรมี error ที่ทำให้ cleanup ล้มเหลว

### Requirement 4: Add Logging Calls to vision.py

**User Story:** ในฐานะผู้พัฒนา ฉันต้องการให้ข้อมูล frame, detection, environment และ event ถูกบันทึกอัตโนมัติขณะประมวลผล เพื่อเก็บสถิติที่ครบถ้วน

#### Acceptance Criteria

1. vision.py ต้อง import ฟังก์ชัน logging จาก `data_logger`
2. ต้องเรียก `log_frame(fps, latency_ms)` หลังจากประมวลผลแต่ละ frame
3. ต้องเรียก `log_detection(...)` สำหรับ detection ที่ valid และ rejected
4. ต้องเรียก `log_environment(...)` ทุก 60 frames
5. ต้องเรียก `log_event(...)` สำหรับเหตุการณ์ สำคัญ (mog2_ready, target_lost, etc.)

### Requirement 5: Verify All Systems Initialize Without Errors

**User Story:** ในฐานะผู้ทดสอบ ฉันต้องการให้แอปพลิเคชันสามารถเริ่มต้นได้โดยไม่มี error ทั้งหมด

#### Acceptance Criteria

1. main.py ต้องเริ่มต้นได้สำเร็จ
2. ไม่มี import errors หรือ initialization errors
3. Logger ต้องพร้อมใช้งานเมื่อ app ทำงาน
4. Dashboard ต้องสามารถเข้าถึงได้ผ่าน browser

## ศัพท์เฉพาะ (Glossary)

- **Logger**: ระบบบันทึกข้อมูล detection, performance, environment และ event
- **Logger Routes**: Flask API endpoints สำหรับการเข้าถึงข้อมูล logging
- **Dashboard**: Web UI แสดงข้อมูลแบบเรียลไทม์
- **vision.py**: โมดูลหลักที่ประมวลผลภาพและตรวจจับวัตถุ
- **log_frame**: ฟังก์ชันบันทึกข้อมูลประสิทธิภาพ (FPS, latency)
- **log_detection**: ฟังก์ชันบันทึก detection result
- **log_environment**: ฟังก์ชันบันทึกข้อมูลสภาพแวดล้อม (brightness, contrast, etc.)
- **log_event**: ฟังก์ชันบันทึกเหตุการณ์สำคัญ

