# A real L4 example — authentication system

This set came from real work: it started as a Login module holding seven mixed-up scenarios and
grew into a full set of 12 modules / 64 scenarios / 18 files.
Use it as a reference for what L4 output looks like — not as something to copy wholesale, since
the business rules (TTLs, attempt counts, policies) differ in every project.

The deliverables were written in Thai because that is the team's working language; the structure
is what transfers.

---

## Module list and type distribution

| # | Module | Code | Scenarios | Happy | Alt | Error | Edge | Sec |
| ---| ---| ---| ---| ---| ---| ---| ---| --- |
| 1 | Register | SC-REG | 6 | 1 | 1 | 3 | — | 1 |
| 2 | Email Verification | SC-VERIFY | 4 | 1 | 1 | 2 | — | — |
| 3 | Login (email + password) | SC-LOGIN | 5 | 1 | 1 | 2 | — | 1 |
| 4 | Google OAuth | SC-OAUTH | 5 | 2 | 1 | 1 | — | 1 |
| 5 | Two-Factor Authentication | SC-MFA | 6 | 2 | 2 | 1 | — | 1 |
| 6 | Forgot / Reset Password | SC-PWD | 6 | 2 | — | 3 | — | 1 |
| 7 | Session & Token | SC-SESSION | 6 | 1 | — | 1 | 2 | 2 |
| 8 | Logout | SC-LOGOUT | 4 | 1 | 1 | — | 1 | 1 |
| 9 | Account Security | SC-ACC | 5 | 2 | 3 | — | — | — |
| 10 | Authorization Guard (RBAC) | SC-AUTHZ | 5 | 1 | — | 1 | 1 | 2 |
| 11 | Security & Abuse Prevention | SC-SEC | 6 | — | — | — | — | 6 |
| 12 | Edge & Resilience | SC-EDGE | 6 | — | — | — | 6 | — |
|  | **Total** | | **64** | **14** | **10** | **14** | **10** | **16** |

Distribution: Happy 22% / Alternate 16% / Error 22% / Edge 16% / Security 25%.
Security runs above the ~15% target deliberately, because authentication is where a miss costs
most — and that reason is written into the document so readers don't think the mix is an accident.

**Structural note:** modules 11 and 12 are *cross-cutting* — they aren't tied to one screen.
Giving Security and Edge their own modules gives a home to the scenarios that span every flow
(brute force, CSRF, injection, boundary values, clock skew) instead of forcing them into a module
where they don't belong.

---

## One full scenario (Happy Path)

The deliverable is in Thai; the shape is the point.

````markdown
## SC-LOGIN-01 · Login ด้วย Email และ Password

**Type:** Happy Path
**Persona:** Registered User — มีบัญชีในระบบแล้ว
**Pre-condition:** มีบัญชีในระบบ, email verified แล้ว, account ไม่ถูก lock

## Scenario Steps
1. User เข้าหน้า Login เห็น form Email และ Password
2. กรอก Email และ Password ที่ถูกต้อง
3. กด "เข้าสู่ระบบ"
4. ระบบ verify credentials — ถูกต้อง
5. ออก JWT access\_token และ refresh\_token
6. Redirect ไปยังหน้า Loading แล้ว Redirect ไปยังหน้า Space โดยอัตโนมัติ

## Acceptance Criteria
*   Form มี Email field และ Password field พร้อม icon แสดง/ซ่อน
*   ปุ่ม "Sign in" disable จนกว่าจะกรอกครบทั้ง 2 field
*   มี loading state บนปุ่ม ขณะรอ API response
*   Login สำเร็จ redirect ภายใน 1 วินาที
*   มี link "ลืมรหัสผ่าน?" ใต้ password field
*   มีตัวเลือก "จำฉันไว้" สำหรับขยาย token expiry
*   ถ้า account เปิด 2FA ไว้ ระบบไปหน้ากรอกรหัส 2FA แทนการเข้าหน้า Space ทันที
*   Session ใหม่ปรากฏในรายการอุปกรณ์พร้อม device / IP / เวลาที่ถูกต้อง

## Business Logic / Rules
*   Access token อายุ 15 นาที, Refresh token อายุ 7 วัน (30 วันถ้า Remember me)
*   เก็บ refresh\_token ใน httpOnly cookie เท่านั้น ห้าม localStorage
*   Access token เก็บ in-memory เท่านั้น
*   Validate redirect\_url ให้เป็น domain เดียวกัน (prevent open redirect)
*   บันทึก last\_login\_at และ last\_login\_ip ทุกครั้ง
*   Reset failed\_login\_count = 0 เมื่อ login สำเร็จ

## UX/UI
https://www.figma.com/design/xxx?node-id=163-41619
````

Note how all eight criteria are **observable**, while every rule invisible from the screen (token
lifetimes, where tokens are stored, redirect validation) sits in Business Logic. That split is
what makes the QA checklist tickable without opening the code.

## One Security Path scenario

````markdown
## SC-MFA-06 · พยายามข้ามขั้น 2FA (bypass)

**Type:** Security Path
**Persona:** Attacker ที่รู้ password แล้ว — พยายามข้ามขั้น 2FA
**Pre-condition:** รู้ email + password ของ account ที่เปิด 2FA และอยู่ที่ขั้นกรอกรหัส 2FA

## Scenario Steps
1. กรอก password ถูกต้อง มาถึงขั้นกรอกรหัส 2FA
2. พิมพ์ URL ของหน้าที่ต้อง login ตรง ๆ โดยไม่กรอกรหัส
3. เรียก API ที่ต้อง auth ด้วย pre-auth token ที่ได้จากขั้นแรก
4. ปิด tab แล้วเปิดใหม่

## Acceptance Criteria
*   พิมพ์ URL หน้าใน ๆ ตรง ๆ ระหว่างค้างขั้น 2FA ถูก redirect กลับมาขั้น 2FA เสมอ
*   เรียก API ด้วย pre-auth token ได้ 401 ทุก endpoint
*   ไม่มี refresh\_token cookie ถูก set ก่อนผ่าน 2FA
*   ปิด tab แล้วเปิดใหม่ ต้องเริ่มจากกรอก email + password ใหม่
*   กด back แล้ว forward ไม่สามารถข้ามไปหน้า Space ได้
*   ทุกความพยายามข้ามขั้นถูกบันทึกลง audit log

## Business Logic / Rules
*   Server ต้องบังคับ 2FA ที่ชั้น API ทุก endpoint ไม่ใช่แค่ redirect ฝั่ง client
*   pre-auth token มี scope `mfa_pending` เท่านั้น อายุ 5 นาที ใช้ครั้งเดียว
*   ห้ามเก็บสถานะ "ผ่าน 2FA แล้ว" ไว้ฝั่ง client เพียงลำพัง
````

Note the Persona is an Attacker *with something already in hand* ("knows the password"), which
tells whoever runs it what state to set up. And the criteria assert that **the system refuses**,
rather than that it works.

---

## Old bugs → criteria (free regression coverage)

Six pre-existing bugs were each promoted into a criterion.

| Old bug | Became a criterion in |
| ---| --- |
| Forgot-password link doesn't work | SC-PWD-04 |
| One email could request more than 3 reset links per hour | SC-PWD-06 |
| Accounts created via Google could request a password reset | SC-PWD-02 |
| Confirm Password show/hide toggle broken | SC-PWD-03 |
| Reset succeeds but login then fails | SC-PWD-03 |
| Sessions on other devices survive a reset | SC-PWD-03 |

Three of them landed on SC-PWD-03 alone, because all three are symptoms of the same scenario
(reset password via link). Merging like that is more correct than creating one scenario per bug,
which would bloat the set and obscure what the actual flow is.

---

## File layout of the full set

```
00-INDEX.md              4-tier structure + module list + coverage map + test data + bug template
01-register.md .. 12-edge-resilience.md
13-non-functional.md     NFR, 8 areas + pass thresholds
14-test-plan.md          scope, strategy, environment, risks R1-R10, entry/exit, roles, schedule
15-traceability-matrix.md  64-row inventory + distribution + flow×type + bug→scenario
16-test-summary-report.md  closing template
```

The risk matrix from that set, as an example of what an auth system's risks look like:
R1 auth bypass · R2 data leaking across accounts · R3 account takeover via password reset ·
R4 user permanently locked out · R5 sessions not revoked after a password change ·
R6 successful brute force / email spam · R7 broken token refresh blocking all use ·
R8 email never reaching users · R9 minor UX defects · R10 untranslated strings / wrong times
