# Drift Prevention & CI Guardrails

A design system without enforcement decays back into hardcoded values within months —
the EXTRACT-mode audit you just did IS the evidence. Whenever the project has CI (or the
user asks how to keep the system clean), ship guardrails as part of the deliverable.

## Stylelint (CSS side)

Use `stylelint-declaration-strict-value` to require `var()` for every token-governed property:

```json
{
  "plugins": ["stylelint-declaration-strict-value"],
  "rules": {
    "scale-unlimited/declaration-strict-value": [
      ["/color$/", "fill", "stroke", "background-color",
       "font-size", "font-family", "line-height",
       "border-radius", "box-shadow", "z-index",
       "padding", "margin", "gap"],
      { "ignoreValues": ["inherit", "transparent", "currentColor", "0", "none", "auto"] }
    ],
    "color-no-hex": true
  }
}
```

Exempt token files and reviewed invariant/dynamic exceptions (`overrides` on `src/tokens/**`) — primitives are
the one place literals belong.

## ESLint (JS/JSX side)

- Restrict hardcoded inline colors/spacing; allow justified dynamic positioning and token-backed values: `react/review-dom-props` for `style`, or a project rule
  allowing `style` only with token `var()` strings.
- Tailwind projects: `eslint-plugin-tailwindcss` (or v4 equivalent) with
  `no-arbitrary-value` — verify plugin compatibility with the installed Tailwind major; token-backed arbitrary values and dynamic calculations may be valid.
- Restrict imports: primitives module importable only by the semantic layer
  (`no-restricted-imports` on `tokens/primitives`).
- Next.js: review `'use client'` in the presentational component dirs (custom
  `no-restricted-syntax` rule) and verify the client/server module graph and consumer build rather than banning legitimate client boundaries.

## Token integrity script

Add a small check script (runs in CI) that fails on:
- any `var(--...)` reference with no definition (typo'd token)
- cycles, invalid types and undocumented component literals; respect legitimate CSS fallbacks and scopes
- generated output drifting from its declared source
- deprecated aliases past their announced removal date

## CI wiring

- Run linters + integrity script on every PR touching styles/components; failing blocks merge.
- Escapes go in one explicit allowlist file (with reason + owner per line) — visible in
  review, not scattered `/* stylelint-disable */` comments.
- **Legacy codebases (post-EXTRACT): ratchet.** Lint only changed files at first, then
  widen. Turning everything on at once produces 4,000 errors and gets the guardrails
  deleted within a week.
