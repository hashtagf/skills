# Research audit — 2026-10-09

Assessment: useful workflow coverage (four modes, state inventory, packaging and
migration), with correctness gaps that prevent treating the prior text as reliable
production guidance. This review improves instructions; it does not certify generated
libraries. Diagnostic text evals are separate from runtime consumer and usability tests.

| Finding corrected | Primary evidence |
|---|---|
| Focus contrast incorrectly attributed to 2.4.11; separate visibility, obscuration, contrast and AAA appearance | [2.4.11 AA](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html), [1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html), [2.4.13 AAA](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html) |
| 44px presented as universal minimum; clarify AA 24px and exceptions | [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) |
| aria-disabled treated as automatic behavior; boolean presence selectors match false | [MDN aria-disabled](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-disabled) |
| Tabs required automatic activation; modal and non-modal focus contracts conflated | [APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/), [Modal dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| Error-summary focus contract missing | [GOV.UK error summary](https://design-system.service.gov.uk/components/error-summary/) |
| Thai line-height presented as an absolute threshold rather than font/content verification | [W3C Thai layout requirements](https://www.w3.org/TR/2024/DNOTE-thai-lreq-20240430/) |
| Server Components wrongly prohibited from importing Client Components | [Next.js composition](https://nextjs.org/docs/app/getting-started/server-and-client-components) |
| npm pack checked before build; prepublishOnly does not run on pack | [npm lifecycle](https://docs.npmjs.com/cli/v11/using-npm/scripts/) |
| publishConfig.exports override assumed npm-portable | [pnpm publishConfig](https://pnpm.io/package_json#publishconfig), [npm package.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/#publishconfig) |
| Storybook addon install assumed to fail accessibility CI; toolbar lacked defaults/density wiring | [Accessibility tests](https://storybook.js.org/docs/writing-tests/accessibility-testing), [Globals](https://storybook.js.org/docs/essentials/toolbars-and-globals), [Vitest integration](https://storybook.js.org/docs/writing-tests/integrations/vitest-addon/index) |
| Release auth/cost claims too broad | [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/), [GitHub billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages), [Package authentication](https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages) |
| Token interchange and governance missing | [DTCG format](https://www.designtokens.org/tr/2025.10/format/), [GOV.UK contribution criteria](https://design-system.service.gov.uk/community/contribution-criteria/) |

Base-4 spacing, component counts, fixed focus visuals and three mandatory token tiers
are local conventions, not WCAG requirements. Revised guidance preserves existing
contracts and requires relevant evidence instead of enforcing those defaults universally.

## Evidence needed to establish effectiveness

1. Compare old/revised instructions on the same scoped prompts; inspect actual outputs.
2. Build a real small system, render Thai content and test keyboard/zoom/forced colors.
3. Install its clean-build tarball in supported framework consumers; verify CSS/types
   and Next server/client boundaries.
4. Prove accessibility CI fails on a known violation, then passes the corrected fixture.
5. Validate patterns with users and track adoption, defects and upgrade cost.

Report unexecuted checks explicitly. A small diagnostic eval cannot establish general
production readiness, task speed gains or statistically significant improvements.

## Local diagnostic result

Three text prompts compared the original snapshot and revised instructions, one run
each, with four author-graded checks per prompt. Original: 9/12; revised: 12/12.
The differences were explicit AA target-size classification, evidence-based Thai
typography defaults, and a known-violation/recovery proof for the accessibility gate.
The original-output agent independently corrected several erroneous old instructions;
do not count every audited document error as an observed baseline failure.

Outputs, grading and the generated review viewer are local ignored scratch artifacts
under `design-system-builder-workspace/iteration-1/`. No actual UI, npm package or
Storybook test suite was built in this diagnostic run. This result supports the selected
instruction corrections; it is not a general effectiveness benchmark.
