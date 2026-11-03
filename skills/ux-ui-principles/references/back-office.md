# Admin and back-office pages

Design internal and operational tools from the role's task, not from a
component inventory. Ask "why does this person open this page, and what must
they see to finish?" before deciding where cards, tables or buttons go. Complex
applications should reduce clutter without removing capability and keep
important information visible. [S38] Source IDs resolve in [sources.md](sources.md).

The page taxonomy and pattern tables below are **this skill's synthesis** from
Ant Design, IBM Carbon, GOV.UK and NN/g guidance; they are not a joint
classification published by those organizations.

## Eight dimensions to settle per page

| # | Dimension | Question |
|---|---|---|
| 1 | Role | Who uses this page: operator, manager, support, auditor, admin? |
| 2 | Goal | What must they accomplish here? |
| 3 | Information priority | What must be visible immediately, what can wait? |
| 4 | Page structure | Table, detail, form, dashboard, split view? |
| 5 | Actions and decisions | What do they click or decide, and what is the risk? |
| 6 | Density | How much data per view lets experts work fast without clutter? |
| 7 | Interaction and states | Search, filter, loading, empty, error, permission, stale data? |
| 8 | Responsive and accessibility | Does the primary task still work when space or input changes? |

Same data, different jobs: for transactions, an **operator** finds and fixes
exceptions, a **manager** watches trends, risk and team throughput, an
**auditor** traces evidence, change history and responsibility. Their pages may
share components but not layout order.

## Page taxonomy

Pick the primary type first. A page can mix patterns, but one task should lead.

| Page type | Primary goal | Layout pattern | Local layout IDs |
|---|---|---|---|
| Overview dashboard | Understand the situation | Summary → trends → exceptions (operators: exceptions first) | D01 |
| Monitoring | Detect problems quickly | Health → alerts → investigation | D04 |
| List / CRUD | Find and manage records | Search → filter → table → bulk actions | A01 |
| Record detail | Understand one record | Header (identity, status) → key facts → sections → history | A02 |
| Create / edit | Enter correct data | Grouped form → validation → save | A05, P04 |
| Approval / review | Decide with confidence | Evidence → decision → confirmation | A03 |
| Inbox / task queue | Work through items continuously | List → detail → actions → next item | P01 |
| Analytics / report | Analyze and compare | Scope → charts → breakdown → drill-down | D02, D03, D05 |
| Workflow | Track a multi-step process | Progress → current step and owner → history | P02 |
| Settings | Configure without mistakes | Categories → controls → save feedback | U03 |
| Access / permissions | Manage rights safely | Subjects → roles → effective access | A04 |
| Audit log | Investigate past events | Search → event timeline → before/after detail | — (see below) |

## Group A — situation and analysis

| Page | Prioritize | Common failure |
|---|---|---|
| Dashboard | Decision KPIs with comparison (target, previous period), change, items needing action | A wall of numbers with no next action |
| Monitoring | Health status, severity, impact, duration, shortcut to investigate | Many charts while the real incident is not prominent |
| Analytics | Time range, segment, comparison, trend, breakdown, drill-down | Attractive charts that do not answer the business question |

Visualization pages should move from overview to filtering and detail, place
key information prominently and pick chart types that match the data's
meaning. [S41] Every KPI needs units, time window, freshness and a comparison;
distinguish zero, missing and stale data (see [do-and-dont.md](do-and-dont.md)).

Order by role. If people arrive to clear backlog, "requires attention" goes
first; if they arrive to analyze trends, charts lead.

## Group B — managing data

| Page | Prioritize | Common failure |
|---|---|---|
| List / CRUD | Search by real identifiers, useful filters, sort, column priority, bulk actions | Every database column shown regardless of task |
| Detail | Identity, status, key facts, related objects, history | Important facts buried several tabs deep |
| Create / edit | Field grouping, input order, inline validation, save behavior | Multi-column forms that are hard to scan and complete |

Data-table users typically find records, compare them, view or edit details,
and take actions on rows. [S39] Separate table-level tools (search, filters,
batch actions) from row-level actions, and offer density options for expert
use. [S40] Detail pages should show information directly where reasonable and
group it by relationship; use tabs only when content is genuinely complex and
separable. [S41]

Table rules (project recommendations):

- Default sort matches the task (oldest pending first for queues).
- First column identifies the row in users' terms; numeric columns right-aligned
  with tabular figures; status as text plus color, never color alone.
- Bulk selection states whether it covers this page or all matches and shows
  the count before acting (see [experience-patterns.md](experience-patterns.md)).
- Preserve filters, sort, page and selection across detail visits and in URL.
- Narrow screens: keep identifier, status and primary value; move the rest to an
  expandable row or detail. Data tables may need two-dimensional scrolling under
  WCAG reflow exceptions. [S05]

## Group C — decisions and continuous work

| Page | Prioritize | Common failure |
|---|---|---|
| Approval / review | Decision evidence, risk with reasons, consequence of approve/reject | Evidence spread across several pages |
| Inbox / queue | Priority, assignment, SLA, current item, next item | Leaving and re-entering detail pages for every item |
| Workflow | Current step, owner, dependencies, status, next action | A progress bar that hides who the work is waiting on |

Approval pages answer "should I approve?", not just "what is this record?".
Order: amount/subject → evidence (identity, risk reasons, mismatches) →
history → decision. For legal, financial or data-changing submissions, make the
action reversible, checked or confirmed; [S48] a check-answers summary before
commitment lets people review and change details. [S43] Require a reason for
rejection when the reason is communicated or audited. After a decision, move to
the next item. Long multi-part work benefits from a task list with statuses and
dependencies. [S42]

## Group D — configuration and accountability

| Page | Prioritize | Common failure |
|---|---|---|
| Settings | Category, description, default, scope, save state | Unclear whether a change applies instantly or after Save |
| Permissions | Subject/role, effective permissions, scope, risk, history | Role names shown without what the user can actually do |
| Audit log | Actor, action, timestamp with time zone, target, before/after, reason | Many events but no way to trace a cause |

Settings must choose deliberately between **instant effect** (toggle applies
immediately; show confirmation and undo where possible) and **submission
effect** (changes apply on Save; show unsaved state and warn on leave),
based on how values relate and their consequences. [S41] Never mix both
behaviors in one group without visual distinction.

Permission pages show **effective access** (what this person can do, from which
role or grant), highlight high-risk rights, and record who changed what. Audit
logs are append-only, filterable by actor, action, target and time, and show
before/after values and the stated reason.

## Choosing a structural pattern

| Pattern | Suits | Avoid when |
|---|---|---|
| Table | Comparing many records across several attributes | Records have very different structures |
| Card grid | Exploring or summarizing groups visually | Users must compare numbers across many items quickly |
| List–detail | Stepping through many items continuously | Detail needs most of the screen for long, focused work |
| Side drawer | Short view/edit, then return to the same context | Complex tasks needing several sections or long forms |
| Full page | Focused, data-heavy or multi-step work | Small edits that should not lose context |
| Tabs | Separate categories not needed at the same time [S21] | Users must compare information across tabs |
| Step form | Ordered work validated per step | Short tasks or information best seen together |

List–detail layouts adapt between multiple panes and a single pane depending on
available width. [S46] On narrow screens provide an explicit "back to list" and
preserve list position.

## System-wide consistency for admin products

Consistency means shared interaction rules and vocabulary, not identical
layouts. Record these in [design-context.md](../assets/design-context.md):

| Area | Define |
|---|---|
| Navigation | Sidebar groups, breadcrumbs, page hierarchy, active state |
| Page header | Title, description, status, freshness, primary action placement |
| Content width | Reading pages vs full-width tables |
| Spacing | Section, group and field spacing tokens |
| Typography | Title, label and value hierarchy; tabular numerals |
| Density | Compact / comfortable / expanded and who uses each |
| Action hierarchy | One primary per region; secondary; destructive styling and confirmation rules |
| Status vocabulary | One name and color per status across all pages |
| Feedback | Success, error, loading, empty, no-permission and stale-data patterns |
| Accessibility | Keyboard model, focus, contrast, zoom/reflow, screen-reader names |

## Page review checklist (10 items)

Use as a review aid, not a certification. Score each pass / partial / fail with
evidence.

1. **Task clarity** — the page's purpose is obvious on arrival.
2. **Information priority** — critical information is seen before secondary.
3. **Pattern fit** — table/form/cards/split view matches the task.
4. **Action visibility** — the primary action is findable and its result clear.
5. **Efficiency** — repeated work needs few clicks and context switches.
6. **Density** — amount of data suits the role and frequency of use.
7. **States** — loading, empty, error, success, permission and stale states exist.
8. **Responsive** — small screens, zoom and long data still work.
9. **Accessibility** — keyboard, readable text, visible focus.
10. **Consistency** — statuses, navigation, components and behavior match other pages.

After review, test real tasks with representative users and measure completion,
time on task, errors and requests for help (see [measurement.md](measurement.md)).

## Do / Don't

| Do | Don't |
|---|---|
| Order the page by the role's reason for arriving. | Copy one dashboard layout for operators, managers and auditors. |
| Put decision evidence and consequences beside approve/reject. | Make reviewers open three systems to find KYC and history. |
| Use list–detail and auto-advance for queues. | Force a full page load and return trip per item. |
| State instant vs submission effect for each settings group. | Leave users guessing whether a toggle already applied. |
| Show effective permissions and their source. | Show only a role name and expect admins to remember what it grants. |
