# Patterns: turn intent into behavior

Flow, form, state, navigation, destructive-action, data-work, performance and
trust patterns for an active flow decision. These are synthesized project
recommendations unless a source or criterion is named. Adapt official-system
examples to the product context. Apply relevant states, not a fixed matrix to
every decorative element.

## Forms

Ask only for needed information, explain unfamiliar requirements, identify
optional fields, and allow uncertainty when it is a meaningful answer. Reuse
already-provided answers within the journey when safe. GOV.UK's question-page
pattern is a service-context starting point, not a universal instruction to
split every form. Group fields by the user's decision, not backend payload
shape; group related fields when users need to compare or edit them together. [S17]

Use persistent labels, explicit formats and contextual hints; placeholders are
examples, not the only field name. Choose controls by answer type and data
constraints. Permit valid international names/addresses rather than imposing
arbitrary ASCII rules. Keep input on validation failure. Avoid validating
untouched fields while typing; choose timing that supports recovery without
interrupting legitimate partial input.
[S18; timing outside GOV.UK is a project decision]
Full rules (required/optional marking, placeholders, validation timing): [forms.md](forms.md).

Identify each invalid field and explain the specific problem and the correction
using the field's terminology. Separate user-correctable validation from service
outages or ineligibility. [S19] For long forms, pair inline errors with a linked
error summary when it helps navigation; connect summary links to the affected
fields and focus the summary after failed submission when using this pattern. [S20]

Preserve valid input after server rejection or connection failure. Explain
conflicts without overwriting user edits or pretending a retry is harmless.
For a blocked action, expose the unmet prerequisite or permission reason.
Do not disclose protected information merely to explain a denied state.

Example: a profile save fails because the network disappears. Keep the edits,
show that saving failed, and offer retry. Do not reset the form or display
"Saved" because the client accepted the button click.

Success should identify what was completed and what happens next. Irreversible
submission: see [Destructive and consequential actions](#destructive-and-consequential-actions).

## State specification

For each critical screen/control, assess the following and mark irrelevant rows
N/A with a reason. Avoid inventing visible states that the control does not need.

| State | User question | Specification |
|---|---|---|
| Initial/default | What can I do? | Purpose, controls, required information |
| Hover/focus/pressed | Is this actionable? | Mouse, keyboard and touch feedback |
| Selected/expanded | What is active? | Visible and programmatic state |
| Disabled | Why unavailable? | Reason or prerequisite; distinguish from loading |
| Loading/submitting | Did it start? | Feedback, repeat-action handling, timeout/retry |
| Empty | Why no content? | First use vs no matches vs cleared data; next action |
| Partial/stale/offline | Can I trust this? | Timestamp/context, retained work, recovery |
| Validation/service error | How do I recover? | Specific explanation and safe retry |
| Success | Is it finished? | Result, persistence, next step |
| Permission denied | What access do I need? | Explanation and authorized path forward |

### Async and interrupted operations

| State | Information/action the user needs |
|---|---|
| Initial loading | What is being fetched; stable layout; retry after failure |
| Empty collection | Why it is empty and a relevant first action |
| Filtered no results | Active constraints and a way to adjust/reset them |
| Pending mutation | The action in progress and safe duplicate handling |
| Success | The actual result and next useful step |
| Partial success | Which items succeeded, which did not, and failed-only recovery |
| Failure | Cause when known, retained work, and a viable correction/retry |
| Unknown result | Outcome is unconfirmed; reconcile before resubmitting |
| Stale/conflicting data | Freshness or competing changes and a safe resolution |
| Denied/unavailable | Scope of the restriction and an authorized alternative |

Never display success before the operation is confirmed. Use optimistic
feedback only when rollback is reliable and understandable; define rollback and
reconcile conflicts. For consequential actions, distinguish queued, accepted,
processed, and applied states according to the actual product contract. A
timeout can leave the outcome unknown; blindly retrying can duplicate an operation.

Reserve space for late content to avoid moving controls while a user acts.
Announce important state changes accessibly without turning every minor update
into an interruption; status announcement guidance: [S13]. Use actual progress
only when the application measures it.

## Navigation, task continuity and dialogs

Keep location and scope visible: current section, selected account/project,
filters, and detail context. Use recognizable destination labels and predictable
Back behavior. Preserve useful URLs, filters, scroll, inputs and list state when
returning from a detail view if practical. A visual tab is not always a
navigation tab: a tab typically switches related panels within a context;
choose semantics from whether it changes a document or a panel. GOV.UK notes
tabs can suit repeat users but can hide information from infrequent users. [S21]

Keep common actions close to the object they affect. Use progressive disclosure
for secondary options, while keeping frequently needed controls visible. A menu
with fewer items can still be worse if it hides the operator's main work.

Use a dialog for a focused interruption with a reason. Keep complex workflows on
pages when users need history, deep links or long reading. Implement the APG
keyboard/focus contract when using a modal. [S15]

## Destructive and consequential actions

Name the affected object and scope. In bulk work, distinguish selected visible
rows from every item matching a filter. Explain what can be recovered.

Prefer undo for cheaply reversible actions. For irreversible deletion or a
consequential submission, show the meaningful effect before confirmation and
offer a review step or equivalent protection proportional to risk. Typed
confirmations are appropriate only when the consequence warrants their cost;
they are not a default for ordinary edits.

Keep cancellation and escape behavior clear. Closing a dialog does not mean a
server operation was cancelled. Explain this distinction where it affects safety.

## Dashboards, tables and expert work

Start from decisions: monitor, compare, triage, investigate, or act. Specify data
units, time window, timezone, freshness and uncertainty. Distinguish zero,
missing, unavailable and stale values. Provide comparison baselines when useful.
Use tables for exact lookup/comparison and charts for patterns over dimensions;
provide an accessible alternative for essential chart information.

Make filter scope and active filters visible. State whether selection, counts
and totals refer to the current page, the selection, or all matching records.
Put units in headers or nearby labels. Preview bulk-action consequences and
design partial-failure recovery. Do not make irreversible bulk actions easy to
trigger accidentally merely to reduce clicks.

Preserve sorting, filtering, pagination, selection, and context after a repair
or detail edit. Use density appropriate to repeated comparison tasks. Do not
convert a table to cards solely because the viewport is narrow: retain
meaningful comparison with a scoped scroll region, column priority, or an
explicit alternative view. Keep frequent row actions discoverable and keyboard
reachable.

## Speed and stability

Performance targets, field thresholds and the lab-versus-field caveat are owned by
[i18n and performance](i18n-performance.md); do not restate numbers here. [S22]

Project actions: acknowledge input promptly, avoid duplicate submissions, reserve
media space, prioritize task-critical content, and test slow networks/failures.
Good vitals do not prove that users understand the flow.

## Trust and ethical choices

State price, recurrence, data use and consequences where users decide. Keep
decline/cancel choices understandable and usable. Do not fabricate reviews,
urgency or scarcity. Optimize successful informed tasks, not accidental clicks.
Pair conversion metrics with errors, refunds, cancellations, support burden or
other relevant guardrails. These are this skill's product recommendations.

## Checks for a proposed flow

- Can the actor identify the current scope and predict the next action's result?
- Does the critical path remain usable with a failed request or an interruption?
- Are input and context retained through recovery?
- Are denied, empty, no-results, and unknown outcomes distinguishable?
- Is the most consequential action understandable before it takes effect?

The general usability basis includes [Nielsen's heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).
The examples and tradeoffs here are this skill's working guidance, not measured
user-research findings or guarantees that a particular flow will succeed.
