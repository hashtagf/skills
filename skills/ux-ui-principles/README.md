# ux-ui-principles

Skill สำหรับใช้หลัก UX/UI เปลี่ยนโจทย์ผลิตภัณฑ์เป็นการตัดสินใจที่อธิบายเหตุผล
และตรวจสอบได้ วิจัยแหล่งต้นทางบนอินเทอร์เน็ตวันที่ 8 ตุลาคม 2026

## เรียกใช้

```text
/ux-ui-principles ตรวจ UX checkout นี้ จัดลำดับปัญหาและเสนอวิธีตรวจหลังแก้
/ux-ui-principles ออกแบบ flow สมัครสมาชิก ระบุ loading/error/recovery และ keyboard behavior
/ux-ui-principles research หลักการ navigation สำหรับ dashboard ที่ใช้ทุกวัน พร้อมข้อจำกัด
```

ตอบเป็นภาษาที่ผู้ใช้เลือก รองรับข้อความภาษาไทย และใช้ร่วมกับ
`design-system-builder` หรือ `figma-cli` เมื่อต้องสร้างชิ้นงานในขอบเขตนั้น

## สิ่งที่รวบรวมไว้

| เนื้อหา | เอกสาร |
|---|---|
| Workflow และขอบเขตการใช้งาน | [SKILL.md](SKILL.md) |
| Nielsen heuristics, mental model, signifier, Fitts, Hick–Hyman, IA | [Interaction](references/interaction.md) |
| Hierarchy, typography, grouping, responsive และข้อความไทย | [Visual](references/visual.md) |
| WCAG 2.2 ระดับ A/AA/AAA, ข้อยกเว้น, keyboard และ modal | [Accessibility](references/accessibility.md) |
| Forms, state matrix, recovery, navigation, dashboard และความเร็ว | [Patterns](references/patterns.md) |
| วิธีวิจัย การทดสอบ ตัวชี้วัด และจัดลำดับปัญหา | [Validation](references/validation.md) |
| รายการแหล่งอ้างอิง 36 แหล่งและสถานะหลักฐาน | [Sources](references/sources.md) |
| รูปแบบ design decision, audit และ validation plan | [Templates](assets/templates.md) |
| ตัวอย่าง layout 40 แบบ ใน 8 หมวด | [Layout library](assets/layouts/index.md) |
| ตัวอย่างภาษาไทยแบบเต็ม: checkout, admin records, booking | [Worked examples](assets/layouts/worked-examples.md) |
| ตัวอย่างจาก OpenDesign 16 เว็บไซต์ + 8 templates พร้อมระดับหลักฐาน | [OpenDesign references](assets/layouts/opendesign.md) |

## หลักสำคัญที่แปลงเป็นกติกาใน skill

1. เริ่มจากผู้ใช้ งานที่ต้องสำเร็จ และผลเสียหากผิดพลาด ไม่เริ่มจากเลือกสีหรือ style
2. ระบุสิ่งที่สังเกตจริง สมมติฐาน และสิ่งที่ยังไม่ได้ทดสอบแยกกัน
3. เชื่อมปัญหา → ผลต่องาน → หลักการ → behavior ที่เสนอ → วิธีตรวจ
4. ตรวจ failure/recovery และสถานะที่เกี่ยวข้อง ไม่ประเมินเฉพาะหน้าจอปกติ
5. แยกมาตรฐานที่มีข้อกำหนดออกจาก heuristic และข้อเสนอของโครงการ
6. ใช้ข้อจำกัดของงานวิจัยประกอบ ไม่ตั้งกฎว่าเมนูต้องมี 7 รายการหรือไม่เกิน 3 clicks
7. ไม่อ้างว่าภาพหน้าจอรับรอง WCAG ได้ หรือเปลี่ยน UI แล้ว conversion จะเพิ่มเท่าไร

## ตัวอย่างความแตกต่างที่ต้องรักษา

- WCAG 2.5.8 AA ใช้ 24×24 **CSS px** หรือเข้าเงื่อนไขยกเว้น ไม่ใช่บังคับ 44px ทุกกรณี
- 2.4.11 AA ตรวจว่าตำแหน่ง focus ไม่ถูกเนื้อหาที่ผู้พัฒนาสร้างบังทั้งหมด;
  2.4.13 AAA เป็นเกณฑ์ด้าน appearance ของ indicator
- ค่า text-spacing สำหรับ WCAG เป็นเงื่อนไขทดสอบเมื่อผู้ใช้ปรับ ไม่ใช่ default ที่ต้องใช้เสมอ
- Card sorting ช่วยค้น mental model; tree testing ตรวจ hierarchy; ต้องตรวจ UI จริงเพิ่มเติม
- ผู้ใช้กลุ่มเล็กช่วยค้นปัญหา แต่ไม่ใช่ตัวแทนเชิงสถิติของประชากรทั้งหมด

รายละเอียด แหล่งอ้างอิง และข้อยกเว้นอยู่ในเอกสารแต่ละหัวข้อ
เอกสารนี้เป็น snapshot ของการวิจัย ควรตรวจต้นฉบับอีกครั้งเมื่ออ้างเกณฑ์ปัจจุบัน

## คลัง layout examples

มี 40 แบบ แบ่งเป็น marketing, commerce, dashboards, admin, content/learning,
productivity, accounts/settings และ mobile tasks แต่ละแบบมีโครง wide layout,
การปรับจอเล็ก, สถานะสำคัญ, ข้อแลกเปลี่ยน/กรณีที่ควรหลีกเลี่ยง และ acceptance example
ตัวอย่างเป็น blueprint ที่เขียนขึ้นสำหรับการปรับใช้ ไม่ใช่ภาพหน้าจอสำเร็จรูปหรือผลทดสอบผู้ใช้

```text
/ux-ui-principles เลือก layout สำหรับ admin จัดการคำขอ พร้อม responsive และ error states
/ux-ui-principles ใช้ C04 เป็นจุดเริ่มต้น วาง checkout สำหรับร้านนี้พร้อม acceptance checks
```

## แหล่งตัวอย่างจาก OpenDesign

ค้นคว้าวันที่ 9 ตุลาคม 2026 ทั้ง `opendesign.cc` และ `open-design.ai`
เพิ่ม 24 รายการอ้างอิงที่เชื่อมกับ layout IDs ใน skill: 16 site references และ
8 templates เช่น dashboard, pricing, finance report, kanban และ annotated wireframe
ในจำนวนนี้อ่านรายละเอียดได้ 19 รายการ อีก 5 รายการมีเฉพาะ catalog metadata

เก็บลิงก์ต้นทาง วันที่ตรวจ ข้อจำกัด และ attribution ไว้ทั้ง Markdown และ
[JSON catalog](assets/layouts/opendesign-catalog.json) เพื่อให้ agent เลือกเฉพาะรายการที่เกี่ยวข้อง
ยังไม่ได้ตรวจภาพ/การทำงานของเว็บไซต์ต้นฉบับหรือ import template code และ assets
ตัวเลขรายการทั้งหมดของแหล่งภายนอกเป็น snapshot ไม่ใช่จำนวน template ที่ผ่านการทดสอบ

```text
/ux-ui-principles หา reference จาก OpenDesign สำหรับ SaaS landing แล้วจับคู่กับ layout ใน skill
/ux-ui-principles ใช้ ODA05 เป็น reference ของ kanban พร้อมระบุสิ่งที่ต้องตรวจเพิ่ม
```
