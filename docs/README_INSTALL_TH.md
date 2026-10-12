# Kiro Engineering Kit สำหรับ AIAS

ชุดนี้ช่วยให้ Kiro ทำงานกับ repository อย่างมีขั้นตอน: สำรวจโค้ดก่อนแก้, วางแผน, เปลี่ยนเท่าที่จำเป็น, ทดสอบ และรายงานผลตามจริง

## วิธีติดตั้ง

1. สำรองงานปัจจุบันหรือสร้าง Git branch ก่อน
2. แตก ZIP ที่โฟลเดอร์รากของ repository `ai-as` โดยให้โฟลเดอร์ `.kiro` รวมเข้ากับของเดิม
3. ตรวจสอบว่า `.kiro/specs/phase-a1-integration` เดิมยังอยู่ ห้ามลบหรือเขียนทับ
4. เปิด Kiro ใหม่หรือรีเฟรช workspace แล้วดูส่วน Agent Steering & Skills
5. เริ่มด้วย prompt ใน `Kiro_First_Session_Prompt_TH.md`
6. เรียก skill ด้วย `/architecture-review`, `/systematic-debugging`, `/python-testing-quality`, `/opencv-offline-validation`, `/serial-diagnostics`, `/spec-first-development` หรือ `/release-check`

## มีอะไรอยู่ในชุดนี้

- `.kiro/steering/`: กติกาที่ควรยึดถือในโปรเจกต์
- `.kiro/skills/`: ขั้นตอนทำงานเฉพาะเรื่องที่เรียกใช้เมื่อจำเป็น
- `templates/`: แม่แบบ requirements, design และ tasks สำหรับงานที่มีหลายขั้น
- `Kiro_First_Session_Prompt_TH.md`: prompt สำหรับให้ Kiro สำรวจ repository ก่อนแก้โค้ด

## วิธีใช้งานแนะนำ

1. รัน `/architecture-review` เพื่อสร้างรายการปัญหาที่อ้างอิงไฟล์และบรรทัด
2. เลือกปัญหาเดียวที่มีผลกระทบสูง แล้วใช้ `/spec-first-development` วางแผน
3. ใช้ `/systematic-debugging` หรือ skill ที่ตรงกับงาน
4. ใช้ `/python-testing-quality` และ `/release-check` ก่อนสรุปว่างานเสร็จ

## ข้อกำหนดสำคัญ

- ห้ามบอกว่าทดสอบผ่าน ถ้ายังไม่ได้รันคำสั่งจริง
- อย่าเพิ่ม dependency หรือเปลี่ยน public interface โดยไม่อธิบายเหตุผล
- อย่าเปลี่ยนหลายส่วนใหญ่พร้อมกันโดยไม่มีผลทดสอบแยก
- ตรวจสอบและคงไว้ซึ่งสเปกเดิมของโปรเจกต์ ห้ามลบข้อมูล/ไฟล์เดิมโดยไม่ขออนุญาต
- ชุดนี้มุ่งเน้น maintainability, correctness, offline image processing, diagnostics และการทดสอบอุปกรณ์ทั่วไป ไม่ได้กำหนด workflow สำหรับระบบเล็งอัตโนมัติ การควบคุม recoil หรือการหลบ Anti-Cheat

## หมายเหตุ

ชุดนี้สร้างจากโครงสร้างและข้อมูลที่ระบุไว้ใน README ของ repository ณ ตอนจัดทำ ก่อนแก้โค้ดจริง Kiro ต้องตรวจไฟล์และคำสั่งทดสอบที่มีอยู่ใน branch ปัจจุบันอีกครั้ง
