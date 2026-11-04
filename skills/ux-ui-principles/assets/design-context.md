# Shared design context — template

One project file that every design and implementation agent reads before
deciding, so design, implementation and review work do not make
conflicting choices. Suggested location: `docs/design-context.md` in the
product repository (or the path the project already uses). Keep it short and
current; link to detailed documents instead of copying them.

Create or update it only when the user asks for project documentation or the
host workflow owns such a file. Otherwise state the assumed context in the
answer.

```markdown
# Design context: <product>
Last updated: <date> · Owner: <name/role>

## Product
- Purpose (one sentence):
- Primary outcomes and metrics (+ guardrails):
- Non-goals:
- Platforms: web (browsers) / iOS / Android; supported widths:
- Locales and calendar: e.g. th-TH (Buddhist Era in UI), en-US; time zone rules:
- Accessibility target: e.g. WCAG 2.2 AA
- Regulatory / security constraints:

## Roles
| Role | Goals | Frequency | Device | Key permissions | Cost of error |
|---|---|---|---|---|---|

## Information architecture
- Domain objects and relationships:
- Navigation sections (and which roles see them):
- URL conventions:
- Canonical page per object:

## Vocabulary
| Term | Meaning | Avoid |
|---|---|---|
Status names:
| Status | Meaning | Semantic color | Used on |
|---|---|---|---|
Voice: register, politeness, Thai/English term policy.

## Design system
- Token source (file/package/Figma library):
- Color roles; type roles; spacing scale; radius; elevation:
- Density modes and where each is used:
- Component library and version:
- Approved deviations (with reason):

## Patterns decided
| Situation | Pattern chosen | Reason | Date |
|---|---|---|---|
e.g. Settings save behavior; destructive confirmation; table bulk selection scope;
empty-state wording; session timeout warning; notification deep links.

## Quality bars
- Rigor tier rules (which pages are Critical):
- Performance budgets:
- Required checks before release (design QA list):
- Analytics event naming convention and excluded data:

## Open questions and assumptions
| Item | Risk | How/when to resolve |
|---|---|---|
```
