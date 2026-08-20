# Publishing & Sharing: make the system `npm i`-able

Read this when the design system must be consumed outside its own repo — "publish to npm",
"share ให้ทีมอื่น `npm i` ได้", a second repo wants the package, or the user asks to turn an
existing workspace package into a published one. This extends `packaging.md` (which covers
detection and in-repo shapes); versioning/deprecation semantics live in `operations.md`.

## 0. Pick the sharing channel first

The build is the same everywhere; the channel decides auth, cost, and consumer friction.
Ask which applies (or infer from the repo's remotes/org) before touching config:

| Situation | Channel | Notes |
|---|---|---|
| Open source / public | **npmjs.com public** | Scoped name `@org/ui`; first publish needs `--access public` |
| Private, org already pays npm | **npmjs.com private** | Zero consumer friction beyond `npm login` |
| Private, code lives on GitHub | **GitHub Packages** | Free with the repo; every consumer (and CI) needs a `read:packages` token + `.npmrc` — real friction, say so |
| Enterprise with Artifactory/Nexus/Verdaccio | **that registry** | Publish via `publishConfig.registry`; consumers usually already have `.npmrc` |
| No registry, share now | **git URL or tarball** | `npm i git+ssh://git@github.com/org/ui.git#v1.2.0` or `npm pack` → share the `.tgz`. No semver ranges, no dist-tags; git installs run `prepare`, so the repo must build itself — treat as a stopgap, not the destination |

A monorepo-internal `workspace:*` package (packaging.md shape 1) needs none of this — only
publish when a consumer outside the workspace exists.

## 1. Build pipeline

Published packages ship `dist/`, never raw `src/` (consumers' bundlers won't compile your TS/SFCs).

- **React / Next.js**: `tsup` — `format: ['esm']`, `dts: true`, `sourcemap: true`,
  `external` everything in `peerDependencies`. Add CJS only if a known consumer needs it.
- **Vue 3**: Vite library mode + `@vitejs/plugin-vue`, types via `vue-tsc --declaration`
  (tsup can't emit SFC types).
- **CSS**: `tokens.css` / `theme.css` are copied verbatim into `dist/` (they are the
  framework-independent contract); component CSS imports stay in the JS and are declared via
  `sideEffects: ["*.css"]` so bundlers don't tree-shake them away.
- **Next.js pitfall — verify, don't assume**: bundlers commonly strip `'use client'`
  directives. After building, grep `dist/` for `use client`; if gone, preserve it (tsup:
  `banner` per client entry, or split client components into their own entry). A design
  system that silently loses its directives breaks only at the consumer's build — the worst
  place to find out.

## 2. package.json for the published shape

Complete example — every field here earns its place:

```json
{
  "name": "@org/ui",
  "version": "0.1.0",
  "license": "MIT",
  "type": "module",
  "files": ["dist"],
  "sideEffects": ["*.css"],
  "exports": {
    ".": { "types": "./dist/index.d.ts", "import": "./dist/index.js" },
    "./tokens.css": "./dist/tokens.css",
    "./theme.css": "./dist/theme.css"
  },
  "peerDependencies": { "react": ">=18", "react-dom": ">=18" },
  "peerDependenciesMeta": { "react-dom": { "optional": false } },
  "publishConfig": { "access": "public" },
  "repository": { "type": "git", "url": "git+https://github.com/org/ui.git" },
  "scripts": {
    "build": "tsup",
    "prepublishOnly": "npm run build"
  }
}
```

Rules encoded above, stated once:

- Framework in `peerDependencies`, never `dependencies` — bundling React duplicates it in
  the consumer and breaks hooks.
- `files: ["dist"]` allowlist beats `.npmignore` denylist — new junk stays out by default.
- `types` condition **first** in each export entry; keep the `./tokens.css` export so apps
  can adopt tokens before components.
- `prepublishOnly` makes a stale-dist publish impossible.
- Same-repo promotion: keep the workspace `exports` pointing at `src/` for local dev via a
  `development` condition or `publishConfig.exports` override pointing at `dist/`, so
  workspace consumers keep HMR while the published artifact ships built output.

## 3. Verify before first publish — all four, in order

1. `npm pack --dry-run` — the printed file list **is** the package. No `src/`, stories,
   tests, or `.env`; `dist/` and CSS present.
2. `npx publint` and `npx @arethetypeswrong/cli --pack .` — catch exports-map and types
   resolution bugs that only appear in consumers.
3. **Tarball smoke-install**: `npm pack`, then in a fresh throwaway Vite/Next app
   `npm i ../org-ui-0.1.0.tgz`, import one component + `@org/ui/tokens.css`, run its build,
   render it. A package that has never been installed from its own tarball is a hypothesis,
   not a package — this is the packaging analogue of the skill's render-verify rule.
4. Name check: `npm view @org/ui` → 404 means free. Scope must be an org/user you control.

## 4. Publish mechanics

- First time: `npm login`; scoped-public needs `--access public` (covered by
  `publishConfig` above).
- Prefer publishing from CI with `npm publish --provenance` (npmjs.com) — provenance links
  the artifact to the exact commit/workflow.
- Prereleases on a dist-tag: `npm publish --tag next` — never let a prerelease become
  `latest`.
- **Never unpublish** a version others may use; `npm deprecate @org/ui@"<1.2.0" "msg"`
  instead. Unpublish breaks consumer lockfiles permanently.

## 5. Release automation (Changesets)

For any package with more than one contributor or consumer:

- `npx changeset init`; every PR that changes the package adds a changeset (patch/minor/major
  per the semver table in `operations.md` — token value changes are minor-but-flagged,
  renames/removals major).
- GitHub Actions: `changesets/action` opens a "Version Packages" PR (bumps + CHANGELOG);
  merging it publishes. Publish job needs `NPM_TOKEN` secret and, for provenance,
  `permissions: { id-token: write, contents: read }`.
- Tag releases `v{version}`; the git tag is what makes `npm i git+…#v1.2.0` fallbacks and
  bisecting consumer regressions possible.

## 6. Registry-specific consumer setup

**GitHub Packages** — publisher adds `publishConfig.registry: "https://npm.pkg.github.com"`;
every consumer needs a `.npmrc`:

```
@org:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NPM_TOKEN}
```

with a PAT (`read:packages`) locally and a token secret in CI. Document this in the README —
it is the #1 "works on my machine, fails in CI" cause for GitHub Packages.

**Verdaccio (self-hosted, free)**: `docker run -p 4873:4873 verdaccio/verdaccio`, then
`npm publish --registry http://host:4873` and consumer `.npmrc`
`@org:registry=http://host:4873`. Good for teams that can't use npm private and find
GitHub Packages auth too heavy.

## 7. Consumer README — the install contract

The published README must let a stranger go from zero to a rendered Button. Include, in order:

1. Install: `npm i @org/ui` + peer deps (`npm i react react-dom` if not present) + any
   `.npmrc` setup from §6.
2. Tokens once, at the app root: Next.js → import `@org/ui/tokens.css` in `app/layout.tsx`;
   Vue → in `main.ts`; Tailwind v4 → `@import "@org/ui/theme.css";` in the app's CSS entry.
3. First component: a 5-line copy-paste example.
4. Theming: how to set `data-theme` (from `theming.md`), and the rule that overrides happen
   at the semantic-token layer, not by overriding component CSS.
5. Versioning policy: link the changelog; state that semantic token value changes land as
   flagged minors (so visual diffs on upgrade are expected, not bugs).
