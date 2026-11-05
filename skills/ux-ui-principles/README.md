# ux-ui-principles

Skill สำหรับใช้หลัก UX/UI เปลี่ยนโจทย์ผลิตภัณฑ์เป็นการตัดสินใจที่อธิบายเหตุผล
และตรวจสอบได้ วิจัยแหล่งต้นทางบนอินเทอร์เน็ตวันที่ 8 ตุลาคม 2026

## Framework 6 ระดับ (ใหม่)

สกิลครอบคลุมตั้งแต่ "ควรสร้างอะไร" จนถึง "วัดผลหลังใช้งานจริง" และแยก 6 ศาสตร์ออกจากกัน:
Product · UX · UI · Interaction · Design Engineering · Validation

| ระดับ | ครอบคลุม | เอกสาร |
|---|---|---|
| 1. Product Strategy & Research | ปัญหา หลักฐาน role ตัวชี้วัดความสำเร็จ ข้อจำกัด | [Product discovery](references/product-discovery.md) |
| 2. Experience Architecture | Journey, flow, IA, navigation, การจัดกลุ่มเมนู, URL, permission flow | [Experience architecture](references/experience-architecture.md), [Navigation grouping](references/navigation-grouping.md) |
| 3. Page & Interaction | ประเภทหน้า layout state การกู้คืน UX writing, copy การตลาด, การแสดงค่าข้อมูล | [Back office](references/back-office.md), [Content design](references/content-design.md), [Marketing copy](references/marketing-copy.md), [Patterns](references/patterns.md) |
| 4. Visual & Design System | tokens, type, spacing, component, state, focal point, color, icon | [visual system](references/visual-system.md) Part A, [Components usage](references/components-usage.md), [Component states](references/component-states.md), [design quality](references/design-quality.md) §7 |
| 5. Quality & Engineering | Accessibility, i18n, performance, security/privacy UX | [Trust/Security/Privacy](references/trust-security-privacy.md), [i18n & performance](references/i18n-performance.md) |
| 6. Validation & Improvement | metric, instrumentation, A/B, design QA, รอบปรับปรุง | [Measurement](references/measurement.md), [Validation](references/validation.md) |

ภาพรวมและกระบวนการ Discover → Define → Structure → Design → Verify → Improve อยู่ใน
[Framework](references/framework.md)

**ระดับความเข้มงวด (Rigor tier):** เลือกจากผลเสียที่อาจเกิดเมื่อออกแบบผิด
- **Light:** หน้าอ่านอย่างเดียวหรือความเสี่ยงต่ำ
- **Standard:** flow หลักและหน้าฝั่งลูกค้า
- **Critical:** เงิน การอนุมัติ สิทธิ์ และการลบถาวร

tier เป็นตัวกำหนดว่าต้องตอบข้อไหนใน [Page spec 16 ข้อ](assets/page-spec.md)

**Design context กลาง:** [template](assets/design-context.md) สำหรับไฟล์เดียวของโปรเจกต์
ที่เก็บ role, คำศัพท์, ชื่อ status, tokens และ pattern ที่ตัดสินใจแล้ว
ให้ทุกงานออกแบบ พัฒนา และรีวิว ใช้ข้อมูลชุดเดียวกัน

## Workflow การออกแบบ (phase 0–8)

สกิลทำงานตาม phase: Inspect → Understand → Architect → Explore → Design → Implement → Critique → Verify → Deliver
แต่ละ phase ระบุว่าทำอะไร ใช้เอกสารไหน **ต้องถาม user ตอนไหน** และจบ phase เมื่อไร
แต่ละ mode (ANSWER, RESEARCH, DISCOVER, ARCHITECT, DESIGN, BUILD, AUDIT, ONBOARD, IMPROVE, REFINE) ใช้เฉพาะ phase ที่จำเป็น

| ถาม user เมื่อ | ไม่ถาม (ตัดสินใจเองแล้วติดป้าย assumed) |
|---|---|
| ไม่รู้ role หรืองานหลัก (Standard ขึ้นไป) | spacing, ข้อความร่าง, เลือก component, ชื่อเมนู |
| กฎธุรกิจงาน Critical: ใครอนุมัติ, วงเงิน, ค่าธรรมเนียม, ย้อนกลับได้ไหม | สิ่งที่หาได้เองจาก repo หรือไฟล์ที่แนบมา |
| หน้าตาใหม่: interview 3 รอบ (A ธุรกิจ, B รสนิยมพร้อมภาพ, C ยืนยัน) แล้วเลือก direction | composition ของหน้าทำงานภายใน (เลือกจาก task success) |
| ขยาย scope, เพิ่ม dependency, เปลี่ยน token ทั้งระบบ, เขียนเอกสารโปรเจกต์ | รายละเอียดการ implement ภายใน scope |
| hard gate ไม่ผ่านและแก้ใน scope ไม่ได้ | การ critique (แก้เองใน scope) |

ถามครั้งละไม่เกิน 3 ข้อ (ยกเว้น interview หน้าตาใหม่ ไม่เกิน 4 ข้อต่อรอบ) และทุกข้อมีค่าแนะนำ ถ้า user ไม่อยู่หรือบอกให้ใช้ค่าเริ่มต้น จะไม่หยุดถาม แต่ใช้ค่าแนะนำแล้วสรุป "Decisions to confirm" ไว้ท้ายงาน
รายละเอียด: [Design workflow](references/design-workflow.md)

## หัวข้อเพิ่มเติม (4 พ.ย. 2569)

| เรื่อง | เอกสาร |
|---|---|
| Design foundations: token layers, type scale, spacing, radius, elevation, motion, breakpoint, density, focus, theme | [visual system](references/visual-system.md) Part A |
| เลือก component ให้ถูกงาน (tooltip/popover/dialog, toast/banner, pagination/infinite scroll ฯลฯ) และกติกาการใช้ ~60 component | [Components usage](references/components-usage.md) |
| State ครบทุกแบบ + keyboard contract ตาม ARIA APG + template spec ของ component | [Component states](references/component-states.md) |
| วิธีส่งงานออกแบบ: text wireframe, HTML prototype พร้อม state และ variant, hand-off | [Prototyping](references/prototyping.md) |
| คุณภาพงานออกแบบ: วางแผน → ตรวจแผนเทียบหน้าตาสำเร็จรูป, idea sentence + competitor test, รายการสิ่งที่ทำให้ดู "เป็น template", วิธี critique จากภาพหน้าจอ | [Design quality](references/design-quality.md) |
| หน้าฝั่งลูกค้า: ประเภทหน้า 13 แบบ, ต่างจากหลังบ้านอย่างไร, onboarding, ความน่าเชื่อถือ | [Customer UI](references/customer-ui.md) |
| UX ของฟีเจอร์ AI: เหมาะเมื่อไร, ให้ผู้ใช้ควบคุมตามความเสี่ยง, state ของผลลัพธ์ AI | [AI features](references/ai-features.md) |
| การออกแบบฟอร์ม: ถามอะไร, โครงสร้าง, label, เลือก control, ที่อยู่/เบอร์/บัตรประชาชนไทย, validation | [Forms](references/forms.md) |
| การใช้ icon: เมื่อไรต้องมี label, ชุดเดียว ความหมายเดียว, ขนาด, พื้นที่กด, accessible name | [Iconography](references/iconography.md) |
| Native mobile: iOS/Android, ขอสิทธิ์ในจังหวะที่ใช้, push, deep link, offline, gesture | [Mobile native](references/mobile-native.md) |
| การสื่อสารข้ามช่องทาง: email/SMS/push/in-app | [Notifications](references/notifications.md) |
| Data visualization: เลือกกราฟจากคำถาม, สีในกราฟ, state ของข้อมูล | [Data visualization](references/data-visualization.md) |
| การสร้างและตรวจชุดสี: role ก่อนค่าสี, สีสถานะคงที่, contrast สองโหมด | [Color palette](references/color-palette.md) |
| การตรวจหน้าที่ render จริง + script `render_check.js` และ `contrast.py` (`--css` ตรวจ token ทุกธีมจากไฟล์หน้าเว็บอัตโนมัติ) | [Render verification](references/render-verification.md) |
| ตัวอย่างระบบหลังบ้าน PayOps 4 หน้า + SkillMap (skill matrix) + layout ใหม่ A06 Audit log, A07 Settings, D06 Matrix/heatmap | [Worked examples](assets/layouts/worked-examples-back-office.md) |
| ทิศทางการออกแบบ: แยก 8 มิติ, เลือก page pattern จากคำถามของผู้ใช้, layout composition, คลัง visual style + กติกาผสม, dial variance/motion/density | [Design direction](references/design-direction.md) |
| ความจำด้านดีไซน์: ตรวจโปรเจกต์ก่อนออกแบบ, ลำดับ source of truth, template DESIGN.md พร้อมเหตุผลและ anti-pattern, เลือก specialist skill เฉพาะที่ติดตั้งจริง | [Design memory](references/design-memory.md) |
| แนวคิดจาก Hallmark / Impeccable / Hue / Taste / Interface Design: structural slop และ one strong idea, สกัดภาษาดีไซน์จากแบรนด์, เสนอ 2–3 direction ก่อนสร้าง, script `slop_check.py` ตรวจหน้าตาแบบ template และ `design_md_check.py` ตรวจ DESIGN.md | [Design quality](references/design-quality.md) §2b, [Design memory](references/design-memory.md) §3b, [Design direction](references/design-direction.md) §7 |
| **ค่าเริ่มต้นห้ามข้าม (หน้าเว็บสาธารณะ / หน้าตาใหม่):** interview ก่อนเขียนโค้ด → palette จาก keyword → motion baseline → mobile ที่ออกแบบสำหรับ 390px → render ดู 1440 + 390 | [SKILL.md](SKILL.md) |
| Palette: สูตร OKLCH (neutral ย้อมสีเดียวกับแบรนด์, accent เดียว, ไม่เกิน 2 hue, 70/20/10) + palette ตั้งต้น 8 ชุดตาม keyword ที่ตรวจ contrast ผ่านแล้ว 96/96 | [Color palette](references/color-palette.md) |
| Mobile web: gutter, header, hero, ขนาดตัวอักษร, section, grid, ตาราง, พื้นที่กด, sticky, รูป | [visual system](references/visual-system.md) Part B |
| Motion ของเว็บและแอป: ระดับตาม dial, 10 ประเภท, ลำดับการเคลื่อนไหวบนหน้าเว็บ, reduced motion, performance, motion spec, ตรวจด้วย `render_check --reduced-motion` | [Motion](references/motion.md) |
| Style 18 แบบ, keyword ภาษาไทย/อังกฤษ → style + dial, interview 3 รอบสำหรับหน้าตาใหม่ (A: goal/audience/proof/constraints, B: feel/shape/reference/energy พร้อมภาพ, C: ยืนยัน) แล้วเขียน DESIGN.md ด้วย `design_md.py --wire` | [Design direction](references/design-direction.md) §4, §8, §9 |
| รอบรีวิว: คำสั่งปรับงาน (critique, polish, bolder, quieter, distill ฯลฯ), scorecard visual/UX, hard gate ที่ห้ามส่งงาน | [Review loop](references/review-loop.md) |
| Signal budget (สัญญาณต่อ element ไม่เกิน 2) และตารางวินิจฉัยคำติ "ดูยาก / สีดูยาก / รก / ไม่สวย" | [design quality](references/design-quality.md) §7 |
| กติกา heatmap / matrix: ramp สีอ่อน ตัวอักษรสีเดียว ไม่ใช้ความจางแทนสถานะ, สถานะ live/syncing/stale ของ dashboard ที่ refresh | [Data visualization](references/data-visualization.md) |

## หัวข้อเพิ่มเติม (5 พ.ย. 2569, 0.12.0 และ Unreleased)

| เรื่อง | เอกสาร |
|---|---|
| คลัง direction 58 แบบพร้อมภาพ preview, เลือกตามหัวเรื่องและ feel | [Direction library](references/direction-library.md) |
| หน้าตาหลังบ้าน 16 look (Calm, Dense, Night, High contrast …) พร้อม preview desktop และมือถือ | [Back office](references/back-office.md) |
| สูตรสร้างแต่ละ direction: hard rule, สิ่งที่ห้าม, component ที่ต้องมี, pre-flight (`direction_recipe.py`) | [Direction recipes](references/direction-recipes.md) |
| แปลง direction เป็น token CSS / Tailwind / shadcn พร้อมตรวจ contrast (`export_tokens.py`) | [Tokens to code](references/tokens-export.md) |
| Tailwind v4: token → utility, dark ด้วย `data-theme`, กติกาและการตรวจ | [Tailwind](references/tailwind.md) |
| Component ยาก: editable grid, drag reorder, picker, rich text, tour, autosave form | [Advanced components](references/advanced-components.md) |
| DESIGN.md รูปแบบ Google Labs design.md (YAML tokens + 8 section), สร้างด้วย `design_md.py`, ตรวจด้วย `design_md_check.py` | [Design memory](references/design-memory.md) |
| โปรเจกต์เดิม (brownfield) — mode ONBOARD: ถอด DESIGN.md จากโค้ด (`code_extract.py`, `design_md.py --from-code`), หา drift, baseline audit | [Brownfield](references/brownfield.md) |
| ลำดับการตรวจบังคับ: `--fast` baseline → แก้ทีเดียว → `--fast` ยืนยัน → `--zoom` เต็มครั้งเดียว; panel ปรับค่าสด (`tweaks_panel.py`), รายงานรีวิว HTML (`review_report.py`) | [Render verification](references/render-verification.md), [Review loop](references/review-loop.md) |
| บทเรียนจาก OpenDesign 51 templates (กติกา) และ 25 หน้าที่ render แล้ววัดค่า | [evidence](assets/evidence.md) |

**หมายเหตุการเรียกใช้:** SKILL.md เป็นตัวชี้ทางอย่างเดียว (ตาราง "งาน → ไฟล์ที่ต้องเปิด") กติกาจริงอยู่ใน references
ถ้าต้องการให้ใช้กรอบนี้แน่นอน เรียก `/ux-ui-principles` โดยตรง

**ทดสอบการเลือกไฟล์และการถูกเรียกใช้** (ใช้ API จริง ~$3–4 ต่อรอบด้วย sonnet):
- `python3 evals/route_eval.py` เปิดไฟล์ถูกตาม `expected_reads` ใน `evals/evals.json` ไหม (5 พ.ย. 2569: 1/18 → 14/18 หลังปรับ)
- `python3 evals/trigger_eval.py` ถูกเรียกใช้เองโดยไม่พิมพ์ slash ไหม (5 พ.ย. 2569: 0/12 → 8/12, ไม่ถูกเรียกผิดงาน 6/6)

## เรียกใช้

```text
/ux-ui-principles ตรวจ UX checkout นี้ จัดลำดับปัญหาและเสนอวิธีตรวจหลังแก้
/ux-ui-principles ออกแบบ flow สมัครสมาชิก ระบุ loading/error/recovery และ keyboard behavior
/ux-ui-principles research หลักการ navigation สำหรับ dashboard ที่ใช้ทุกวัน พร้อมข้อจำกัด
/ux-ui-principles discover ฟีเจอร์คืนเงินอัตโนมัติ: ปัญหา หลักฐาน role และ metric
/ux-ui-principles วาง IA และ permission flow ของระบบหลังบ้านชำระเงิน 3 role
/ux-ui-principles เขียน page spec ระดับ Critical สำหรับหน้าอนุมัติถอนเงิน
/ux-ui-principles design QA หน้านี้เทียบกับ spec และระบุสิ่งที่ยังไม่ได้ทดสอบ
```

ตอบเป็นภาษาที่ผู้ใช้เลือก รองรับข้อความภาษาไทย

**ใช้ได้ครบในตัว ไม่ต้องพึ่งสกิลอื่น:** มีทั้งหลักการ, foundations (tokens/type/spacing),
การเลือกและใช้ component พร้อม state และ keyboard, การทำ prototype HTML
และ script ตรวจผล ถ้าโปรเจกต์มี design system อยู่แล้วให้ใช้ของโปรเจกต์ก่อน

## สิ่งที่รวบรวมไว้

| เนื้อหา | เอกสาร |
|---|---|
| Workflow และขอบเขตการใช้งาน | [SKILL.md](SKILL.md) |
| Nielsen heuristics, mental model, signifier, Fitts, Hick–Hyman, IA | [Interaction](references/interaction.md) |
| Hierarchy, typography, grouping, responsive และข้อความไทย | [visual system](references/visual-system.md) Part B |
| ค่าวัดจริงด้านภาพ: น้ำหนัก/tracking/line-height ตามขนาด, อัตราส่วน type, โทนสี, spacing 3 ชั้น, ค่าย radius, motion, ความสมจริงของ content, ค่าภาษาไทย, preset และ craft pass — จาก 35 เว็บจริง + curated.design 18 + Dribbble 18 + Behance 14 + website templates | [visual system](references/visual-system.md) Part C · [Site measurements](assets/evidence.md) · [Gallery study](assets/evidence.md) |
| ข้อตกลงร่วมของ design system สาธารณะ 126 ระบบ: ชั้น token และชื่อ role, focus ring 3px, ค่า radius/breakpoint/density, flow ของงานบริการภาครัฐ (หน้า review, ลิงก์ Change, คงคำตอบ), กฎเรื่อง identity และ provenance | [Design system benchmarks](references/design-system-benchmarks.md) · [คู่มือ 126 ระบบฉบับเต็ม](assets/design-systems/index.md) |
| WCAG 2.2 ระดับ A/AA/AAA, ข้อยกเว้น, keyboard และ modal | [Accessibility](references/accessibility.md) |
| Forms, state matrix, recovery, navigation, dashboard และความเร็ว | [Patterns](references/patterns.md) |
| Do / Don't สำหรับ flow และหน้าจอ พร้อมเหตุผลและวิธีตรวจ | [Do / Don't](references/do-and-dont.md) |
| วิธีวิจัย การทดสอบ ตัวชี้วัด และจัดลำดับปัญหา | [Validation](references/validation.md) |
| รายการแหล่งอ้างอิง 101 แหล่งและสถานะหลักฐาน (S37–S62 เพิ่ม 3 พ.ย., S63–S101 เพิ่ม 4 พ.ย. 2569) | [Sources](references/sources.md) |
| รูปแบบ design decision, audit และ validation plan | [Templates](assets/templates.md) |
| ตัวอย่าง layout 43 แบบ ใน 8 หมวด | [Layout library](assets/layouts/index.md) |
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

มี 43 แบบ แบ่งเป็น marketing, commerce, dashboards, admin, content/learning,
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
