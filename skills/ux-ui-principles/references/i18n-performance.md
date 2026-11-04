# Localization, internationalization and performance

Two quality areas that are cheap to design in and expensive to retrofit.
Source IDs resolve in [sources.md](sources.md). Thai typography and wrapping
are covered in [visual.md](visual.md) and [visual-composition.md](visual-composition.md).

## Internationalization (i18n) — design so localization is possible

Internationalization means designing and building so content can be adapted to
languages, regions and cultures; localization is the adaptation itself. [S50]
Decide supported locales at level 1, not after build.

| Area | Design rule | Check |
|---|---|---|
| Language declaration | Set the page language and mark passages in another language [S49] | `lang` on `<html>`; `lang` on mixed-language parts that a screen reader must pronounce differently |
| Text expansion | Layouts survive longer and shorter translations; no fixed-width buttons or labels | Pseudo-localize or test the longest locale at narrow width and 200% zoom |
| Concatenation | Never build sentences from fragments; word order differs by language | Strings are full sentences with named placeholders |
| Plurals and gender | Use plural/gender-aware message formatting | Test 0, 1, 2, many |
| Dates and times | Format by locale; show time zone when users or data cross zones; avoid ambiguous numeric dates | "3 พ.ย. 2569 14:32 (GMT+7)" vs "3 Nov 2026 07:32 UTC" |
| Calendars | Thai audiences may expect Buddhist Era (พ.ศ.); APIs and exports usually use Gregorian | Label the era where ambiguity matters; store ISO dates |
| Numbers and currency | Locale-aware separators; currency code or symbol placement; tabular figures in tables | ฿125,000.00 / THB 125,000.00 consistently |
| Names | Don't assume first/last order or that everyone has both; allow long names and diacritics | Single "ชื่อ-นามสกุล" field where splitting isn't needed |
| Addresses and phone | Use country-appropriate formats; don't force US-style state/ZIP | Thai address: จังหวัด/อำเภอ/ตำบล/รหัสไปรษณีย์ where relevant |
| Sorting and search | Locale-aware collation; Thai sorting and search ignoring tone-mark variants if users expect it | Test with Thai and mixed-script data |
| Direction | Support right-to-left if any target locale needs it; use logical CSS properties (`margin-inline-start`) | Mirror layout in an RTL locale |
| Icons and imagery | Avoid culture-specific gestures, text inside images, flags as language selectors | Language selector shows language names in their own script |
| Input | Support IME, non-Latin keyboards and paste; don't restrict characters unnecessarily | Type and paste Thai, Chinese and emoji into name fields |

### Language switching

- Remember the choice; don't infer language only from IP location.
- Show each language in its own name ("ไทย", "English").
- Keep the user on the same page after switching.

## Performance as user experience

Slow loading and slow response to input are usability failures. Core Web
Vitals measure loading (Largest Contentful Paint), responsiveness (Interaction
to Next Paint) and visual stability (Cumulative Layout Shift); "good" targets
are assessed at the 75th percentile of page loads. [S22, S54] Verify current
thresholds at the source before quoting them as requirements.

| Concern | Design decision | Check |
|---|---|---|
| Perceived speed | Show page structure immediately; skeletons that match the final layout for content regions | Throttled network recording; no layout jump when data arrives |
| Layout stability | Reserve space for images, ads, banners and async content | CLS in field or lab data; manual scroll test on slow network |
| Input response | Immediate visual feedback on press (pressed state, inline spinner) even if work continues | INP in field data; no frozen UI on large tables |
| Long operations | Progress with what is happening; allow leaving and returning for jobs > a few seconds | Background job pattern with notification on completion |
| Optimistic updates | Use only when failure is rare and reversible; reconcile and explain if it fails | Simulate server rejection after optimistic UI |
| Large data | Paginate or virtualize; server-side filter/sort for big tables; don't load all rows to filter in the browser | Test with production-scale fixtures |
| Images and media | Right size per viewport; lazy-load below the fold | Network panel on mobile profile |
| Offline / poor network | Decide per task: block, queue, or read-only cache; show connectivity state | Toggle offline during a form submit |

### Performance budget in the page spec

For Standard and Critical tiers, write a target in the page spec, for example:
"LCP ≤ 2.5 s and INP ≤ 200 ms at p75 on mid-range Android over 4G for the
withdrawal queue; list of 50 rows renders without visible jank." Name the
measurement source (field data, lab test) and state when it has not been measured.

## Do / Don't

| Do | Don't |
|---|---|
| Decide locales, calendar and currency rules before building. | Hard-code "Nov 3, 2026" formats and translate later. |
| Use complete sentences with placeholders. | Concatenate "คุณมี " + n + " รายการ". |
| Reserve space for async content. | Let the confirm button jump as a banner loads. |
| Give immediate feedback on input even for slow work. | Leave a button unresponsive for two seconds with no state. |
| Measure with field data where possible and state the source. | Claim a page is "fast" from a developer laptop on Wi-Fi. |
