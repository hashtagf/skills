# Administration and back office

Original illustrative layouts for adaptation, not validated production designs.
Read [the selection guide](index.md) before choosing a pattern. Boxes indicate
content groups and priority, not fixed pixel geometry or implementation components.
Use [the shared specification](specification.md) for accessibility, states and tokens.

## A01: Record management

**Task:** Search, select and act on many records.

**Wide layout:**

```text
Workspace navigation | Search + filters
Table + selection | Bulk actions
Pagination | Record detail route
```

**Compact behavior:** Keep key identifiers and actions; offer details without losing filters.

**Applicable states:** Empty; filtered empty; loading; selection; bulk partial failure.

**Avoid / adapt:** Avoid ambiguous select-all scope and silently discarded selections.

**Acceptance example:** Check page-only vs all-matching selection and partial-result recovery.

**Customize:** Substitute real content, labels and permission rules; apply existing
tokens and the actual data model. Record why this structure serves the user task.

## A02: Record detail

**Task:** Understand and edit one object with its history.

**Wide layout:**

```text
Object identity + status | Main actions
Details | Related items
Activity/history | Edit or archive route
```

**Compact behavior:** Stack identity/actions, details and history; preserve return context.

**Applicable states:** Read-only; editing; unsaved; conflict; archived.

**Avoid / adapt:** Avoid treating history as editable current state.

**Acceptance example:** Check edits, permissions, concurrency handling and return to prior list.

**Customize:** Substitute real content, labels and permission rules; apply existing
tokens and the actual data model. Record why this structure serves the user task.

## A03: Approval workbench

**Task:** Review evidence and approve or reject a request.

**Wide layout:**

```text
Review queue | Selected request
Evidence + policy context | Decision panel
Reason + consequences | Audit history
```

**Compact behavior:** Separate reading from final decision; keep evidence accessible.

**Applicable states:** Assigned/unassigned; missing evidence; decided; concurrent decision.

**Avoid / adapt:** Avoid one-click irreversible decisions without context.

**Acceptance example:** Check authority, recorded rationale and no accidental repeat decision.

**Customize:** Substitute real content, labels and permission rules; apply existing
tokens and the actual data model. Record why this structure serves the user task.

## A04: Access management

**Task:** Assign roles and understand the resulting access.

**Wide layout:**

```text
Member list | Invite
Selected member | Role and permission summary
Changes preview | Apply + history
```

**Compact behavior:** Focus each edit on one member or clearly defined selection.

**Applicable states:** Pending invite; revoked; unauthorized; save failure.

**Avoid / adapt:** Avoid showing an editable control users cannot legitimately apply.

**Acceptance example:** Check effective permission changes and prevention of unintended lockout.

**Customize:** Substitute real content, labels and permission rules; apply existing
tokens and the actual data model. Record why this structure serves the user task.

## A05: Import wizard

**Task:** Map data and review effects before applying an import.

**Wide layout:**

```text
File + requirements | Upload
Column mapping | Validation results
Preview changes | Import status + result
```

**Compact behavior:** Use steps with back navigation and retained mappings.

**Applicable states:** Invalid file; mapping error; partial rows; pending; partial result.

**Avoid / adapt:** Avoid importing before consequences and rejected rows are visible.

**Acceptance example:** Check mapping, duplicate policy, resumable recovery and rejected-row reporting.

**Customize:** Substitute real content, labels and permission rules; apply existing
tokens and the actual data model. Record why this structure serves the user task.



## A06: Audit log

**Task:** Find out who changed what, when and why, and trace a cause.

**Wide layout:**

```text
Search (ID, actor, target) | Filters: action, actor, date range
Day-grouped event timeline: time | actor + role | action · target
Expanded event: before → after values | reason | source (UI/API/system)
```

**Compact behavior:** One event per row (time, actor, action); expand in place for before/after; filters in a sheet.

**Applicable states:** No events; filtered empty; loading more; export in progress; permission-restricted fields redacted.

**Avoid / adapt:** Avoid editable or deletable entries; corrections are new events. Avoid raw JSON diffs as the only view.

**Acceptance example:** Starting from a record ID, an auditor finds the change that set a value and sees actor, time with time zone, reason and previous value.

**Customize:** Map real event types and retention rules; decide which fields are redacted per role. See [back-office.md](../../references/back-office.md).

## A07: Settings with save behavior

**Task:** Change configuration safely, knowing when changes take effect.

**Wide layout:**

```text
Category list | Section heading + description
              | Setting rows: label, explanation, current value, control
              | (submission groups) Unsaved banner → Save / Discard
              | Last changed by · when
```

**Compact behavior:** Category list becomes a first screen; each category opens its own page with Back.

**Applicable states:** Instant-effect saved/failed per row; submission group unsaved/saving/saved/failed; dependent setting disabled with reason; no permission (read-only with explanation).

**Avoid / adapt:** Avoid mixing instant and submission effect in one group without distinction; avoid toggles inside forms that save later.

**Acceptance example:** Change a limit, navigate away, and see an unsaved-changes warning; save, then find the change in the audit log.

**Customize:** Decide instant vs submission per group from dependencies and consequence; record it in the design context.
