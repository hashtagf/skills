# Form design

Forms are where most tasks succeed or fail. This file is the full form
reference; [patterns.md](patterns.md) and [experience-patterns.md](experience-patterns.md)
hold the short summaries. Source IDs resolve in [sources.md](sources.md).

## 1. Decide what to ask

- Ask only for information the task or law needs. For each field, write why it
  is needed and what happens if it is wrong. Remove fields nobody can justify.
- Reuse what the service already knows; don't ask twice in one journey
  (WCAG 3.3.7 Redundant Entry, with exceptions). [S11]
- Mark the minority: if most fields are required, mark the optional ones
  ("(ไม่บังคับ)"); if most are optional, reconsider the form.
- Allow honest uncertainty ("ไม่ทราบ", "ไม่มี") when it is a meaningful answer.

## 2. Structure

| Decision | Guidance |
|---|---|
| One page or many | Long or branching forms for occasional users: start with one question per page. [S17] Short forms or forms experts edit often: keep on one page so values can be compared. |
| Layout | Prefer a single column; it gives one reading path and fewer skipped fields. [S83] Place short related fields on one row only when they form a unit (date parts, first/last name if split). |
| Grouping | Group by the user's decision, with a heading or `fieldset`/`legend` per group; not by backend payload. |
| Order | Follow the order users think in (who → what → when → how to pay), easiest and most certain first. |
| Progress | For multi-step forms show step names and position; allow going back without losing data. Use a task list when parts can be done in any order. [S42] |
| Review | For consequential submissions, check-answers before submitting. [S43, S48] |

## 3. Labels, hints and help

- Every control has a visible, persistent label (WCAG 3.3.2). [S65] Placeholder
  text is not a label; it disappears while typing and often has low contrast. [S68, S82]
- The accessible name must contain the visible label text so voice users can
  say what they see (WCAG 2.5.3). [S64]
- Labels sit above the field in single-column forms; this survives long Thai
  labels, translation and narrow screens.
- Hints go between label and field, connected with `aria-describedby`; explain
  format or why the data is needed, before the user makes a mistake.
- Field width suggests expected length (postcode short, address long). [S68]
- Use help links or expandable details for rare questions; don't hide essential
  rules in tooltips.

## 4. Choose the right control

| Answer type | Control | Notes |
|---|---|---|
| One choice from 2–6 visible options | Radios [S70] | All options visible; no default unless one is clearly right and harmless |
| Several choices | Checkboxes [S70] | Add "ไม่มีข้อใดตรง" option when "none" is a real answer |
| One choice from many known options | Select or autocomplete | Select for ~7–15 stable options; autocomplete/combobox for long lists (provinces, banks) |
| Yes/no that applies immediately | Switch | Only for settings with instant effect; use checkbox in forms submitted later |
| Short free text | Text input with correct `type`, `inputmode`, `autocomplete` [S66] | `inputmode="numeric"` for codes, `type="email"`, `type="tel"` |
| Long free text | Textarea with visible character limit if any | Show remaining count only near the limit |
| Known date (birth date) | Three fields day/month/year or a typed field [S69] | Date pickers are slow for distant dates |
| Date near today / availability | Calendar or list of available dates | Show unavailable dates as such, with reason |
| Number with unit | Input + unit label outside the field | Accept users' formatting (commas, spaces) and normalize |
| File | File input with type/size rules stated up front | Show upload progress, allow remove/replace |

Avoid custom controls when a native one works; custom ones must replicate
keyboard, focus and screen-reader behavior (see [accessibility.md](accessibility.md)).

## 5. Common fields

| Field | Guidance |
|---|---|
| Name | Single or multiple fields depending on user and system needs; a single field accommodates the widest range of names; allow any characters and long names; avoid asking for title [S71] |
| Address | Use the country's structure; Thai: บ้านเลขที่/อาคาร, ถนน/ซอย, ตำบล/แขวง, อำเภอ/เขต, จังหวัด, รหัสไปรษณีย์; postcode lookup can prefill but must be editable |
| Phone | Accept spaces, dashes and +66; normalize on the server; explain use ("ส่ง SMS ยืนยัน") [S71] |
| Email | `type="email"`, `autocomplete="email"`; don't ask to type twice — show it back for review instead [S71] |
| National ID | 13 digits; accept with or without dashes; validate checksum on blur; mask after entry if sensitive |
| Money | Show currency; right-aligned in tables but left in forms is fine; allow decimals only if valid |
| Password | Allow paste and password managers; show/hide toggle; state rules up front; no arbitrary maximum [S12] |
| OTP | `autocomplete="one-time-code"`, `inputmode="numeric"`; one field rather than six boxes unless tested; resend with timer |

Set `autocomplete` tokens for personal data fields so browsers can fill them
(WCAG 1.3.5). [S66]

## 6. Validation

| When | Do |
|---|---|
| Before | Constraints and good defaults; hints with format; disable impossible options with reason |
| While typing | Only for constraints the user is clearly building toward (password rules checklist, character count) |
| On leaving a field | Format and obvious errors, only after the user has typed something; don't flag empty untouched fields |
| On submit | Full validation; error summary at top linking to each field, focus moved to summary; inline message at each field [S18, S20] |
| Server-side | Same messages as client; keep all entered values; distinguish user-fixable errors from service failures [S19] |

Error messages say what is wrong and how to fix it, in the field's own words
("ใส่เบอร์มือถือ 10 หลัก เช่น 081 234 5678"), not "ข้อมูลไม่ถูกต้อง".
Associate each message with its field (`aria-describedby`, `aria-invalid`).
Use an icon plus text, never color alone (WCAG 1.4.1). [S67] See
[content-design.md](content-design.md) for wording.

Inline real-time validation that fires too early annoys users and can
interrupt legitimate input; validate after the field is completed unless the
rule is incremental. [S84]

## 7. Submission and after

- Primary button names the action ("ส่งคำขอ", "ชำระเงิน ฿1,250"); one primary per form.
- Prevent double submission; show pending state on the button.
- Preserve input on failure, timeout or session expiry (save drafts where policy allows).
- Unknown outcome: say the result is being checked; never invite a second payment
  ([experience-patterns.md](experience-patterns.md)).
- Success: confirmation page or message with reference, what happens next, and
  how to change. [S44]
- Leaving with unsaved changes: warn in-page; don't trap users.

## 8. Mobile forms

- Correct keyboard via `type`/`inputmode`; `enterkeyhint` for next/done.
- Keep the focused field and its error visible above the on-screen keyboard;
  sticky buttons must not cover them.
- Targets follow platform guidance (iOS default 44 pt, Android ≥48 dp; WCAG 2.5.8
  24 CSS px as the web minimum with exceptions). [S07, S74, S78]
- Prefer native pickers for dates and selects on mobile.

## 9. Back-office forms

- Experts edit more than they create: support keyboard flow (Tab order, Enter to
  submit where safe), and show current values clearly in edit mode.
- Settings forms state instant vs submission effect (see [back-office.md](back-office.md)).
- Two-column layouts are acceptable for dense record editing when groups are
  clearly separated and tab order follows reading order; test with real data.
- Show who last changed a record and when, near the save action.

## Form review checklist

1. Every field has a stated purpose; nothing unnecessary is asked.
2. Visible persistent labels; hints before errors; no placeholder-only labels.
3. Single reading path; groups with headings/legends.
4. Control matches answer type; native controls preferred.
5. `autocomplete`, `type` and `inputmode` set for personal data and numbers.
6. Validation timing doesn't flag untouched fields; messages explain the fix.
7. Error summary links to fields on submit; focus goes to it.
8. Input preserved on every failure path; double submit prevented.
9. Works with keyboard only, at 200% zoom and on a phone with the keyboard open.
10. Thai and long values tested; formats accepted as users type them.

## Do / Don't

| Do | Don't |
|---|---|
| Ask only what the task needs and say why. | Collect "nice to have" data in a required field. |
| Use a single column with visible labels above fields. | Use placeholder text as the only label. |
| Accept natural formats and normalize. | Reject "081-234-5678" because of the dashes. |
| Validate after input and explain the fix. | Turn every field red before the user has typed. |
| Keep entered data on every error. | Clear the form after a server error. |
