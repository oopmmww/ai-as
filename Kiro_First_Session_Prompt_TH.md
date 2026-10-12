# Prompt เปิดงานกับ Kiro

อ่าน `.kiro/steering/` และสำรวจ repository ปัจจุบันทั้งหมดที่เกี่ยวข้อง รวมถึง `README.md`, `requirements.txt`, `.github/workflows/`, `.kiro/specs/phase-a1-integration/`, `main.py` และโมดูลที่เกี่ยวข้อง

**รอบนี้ยังไม่ต้องแก้โค้ด** ให้ทำ audit ก่อน โดยรายงาน:

1. โครงสร้างจริงและ data flow ระหว่างโมดูล
2. คำสั่งติดตั้ง/lint/test ที่มีอยู่จริงจากไฟล์ใน repository
3. ความเสี่ยงเรื่อง import, startup/shutdown, thread safety, resource cleanup, error handling, configuration และ logging
4. จุดที่ยังไม่มี tests และความเสี่ยงของการเปลี่ยนแปลง
5. รายการงานเรียง P0/P1/P2 โดยระบุไฟล์/ฟังก์ชันและหลักฐาน
6. แนะนำงานแรกที่เล็กที่สุด พร้อม acceptance criteria และวิธีทดสอบ

อย่าสมมติว่าฟังก์ชันหรือ test มีอยู่ ถ้ายังไม่ได้ตรวจไฟล์ อย่าแก้ไฟล์หรือติดตั้ง dependency ระหว่าง audit นี้ อย่าเพิ่มฟังก์ชันควบคุมเกม/การเล็งอัตโนมัติหรือกลไกหลบ Anti-Cheat ให้เน้นความถูกต้องและความเสถียรของซอฟต์แวร์ทั่วไป
