---
name: figma-cli
description: >-
  Build, edit, render, and verify Figma designs through figma-ds-cli's JSX DSL
  and Figma Desktop bridge. Use this skill whenever a task involves a
  figma-ds-cli project, its Frame/Text/Icon/Rectangle/Image/Instance/Slot JSX,
  `node ~/figma-cli/src/index.js` commands, `var:` token bindings, DESIGN.md
  imports, render or render-batch, or turning design-as-code sources into live
  editable Figma nodes. Also use it when the user asks to create, update,
  re-render, arrange, inspect, export, lint, or screenshot a Figma screen and
  the workspace contains figma-ds-cli JSX—even if they only say “ship this to
  Figma.” This workflow is for the local CLI/Desktop bridge, not Figma MCP.
---

# figma-cli

Use `figma-ds-cli` as a design compiler: JSX files are the editable source of
truth and Figma nodes are generated output. Keep the source reproducible,
render it into the active Figma Desktop file, inspect the result visually, and
iterate until it matches the request.

The JSX resembles React but is a small independent DSL. Do not run it through a
React toolchain or assume CSS/React prop names work.

## Discover the project before changing it

Do not assume a file key, page, collection name, viewport, or directory shape.
Find them from the current project:

1. Locate the relevant `.jsx`, `README.md`, `DESIGN.md`, and preview files.
2. Read the flow's instructions and one nearby screen before authoring a new
   one. Preserve its naming, dimensions, tokens, typography, and file layout.
3. Confirm the CLI location. It is normally `~/figma-cli/src/index.js`; if it
   is absent, search the workspace or ask where figma-ds-cli is installed.
4. Read the installed CLI's `CLAUDE.md` before non-trivial DSL work and
   `REFERENCE.md` before using an unfamiliar command. These files track the
   running engine more reliably than copied command lists.

Use the full command explicitly in reproducible instructions:

```bash
node ~/figma-cli/src/index.js <command>
```

For a short interactive shell session, a function avoids quoting surprises:

```bash
figma_cli() { node ~/figma-cli/src/index.js "$@"; }
figma_cli status
```

## Choose the operation

| User intent | Preferred operation |
|---|---|
| Create or update a composed screen/component | Edit `.jsx`, then `render` |
| Create many similar independent items | `render-batch` |
| Create several distinct screens | Render each source file separately |
| Inspect existing Figma state | `find`, `get`, `inspect`, or `analyze` |
| Change supported properties on existing nodes | `set` or `set-batch` |
| Manage tokens | `var`, `collections`, `tokens`, `import`, or `bind-batch` |
| Check the result | `verify`, then visually inspect the saved PNG |
| Export existing work | `export`, `export-jsx`, or `export-storybook` |

Use `eval` only for Plugin API reads or a narrowly scoped mutation that has no
CLI subcommand. It bypasses the renderer's layout, positioning, and safety
behavior, so it is a poor way to create visual nodes.

## Connect, render, inspect, iterate

Follow this loop for every design mutation.

### 1. Establish the Desktop bridge

Figma Desktop must be open with the target file active.

```bash
node ~/figma-cli/src/index.js status
node ~/figma-cli/src/index.js connect --safe
node ~/figma-cli/src/index.js status
```

Safe mode uses the development plugin. After connecting, ask the user to open
**Plugins → Development → FigCli** if the status still reports no bridge.
Plain `connect` patches Figma Desktop for a faster automatic bridge; use it only
when the user already relies on that mode or asks for it. `unpatch` reverses it.

### 2. Author a source file

Write substantial JSX to a `.jsx` file instead of embedding it directly in a
shell command. Match the project's existing root-frame convention and place
new files beside the related screens.

The core, most reliable DSL set has seven node types (the installed reference
may expose additional shapes):

- `Frame`: auto-layout container
- `Text`: text node
- `Icon`: Iconify/Lucide icon
- `Rectangle`: simple shape
- `Image`: image fill
- `Instance`: component instance
- `Slot`: component slot

A compact example:

```jsx
<Frame name="Account card" w={320} bg="#FFFFFF" rounded={16}
       stroke="#E4E4E7" strokeWidth={1} flex="col" gap={12} p={20}>
  <Text w="fill" size={18} weight="bold" color="#18181B">Account</Text>
  <Text w="fill" size={14} color="#52525B">
    Manage profile and security preferences.
  </Text>
  <Frame flex="row" justify="center" items="center" gap={8}
         bg="#0F766E" rounded={10} px={16} py={10}>
    <Icon name="lucide:settings" size={16} color="#FFFFFF" />
    <Text size={14} weight="semibold" color="#FFFFFF">Open settings</Text>
  </Frame>
</Frame>
```

Common props:

| Concern | DSL props |
|---|---|
| Layout | `flex="row"|"col"`, `gap`, `justify`, `items`, `grow={1}` |
| Padding | `p`, `px`, `py`, `pt`, `pr`, `pb`, `pl` |
| Size | `w`, `h`, `minW`, `maxW`, `minH`, `maxH`; `"fill"` or `"hug"` where supported |
| Color | `bg`, `stroke`, `color`; hex or `var:<token>` |
| Shape/effects | `rounded`, corner-specific radii, `shadow`, `blur`, `opacity`, `overflow`, `rotate` |
| Text | `size`, `weight`, `font`, `color` |
| Positioning | `position="absolute"`, `x`, `y`; give absolute nodes a `name` |

Check `~/figma-cli/CLAUDE.md` for accepted values and advanced features such as
gradients, constraints, wrapping layouts, image fills, instances, and slots.

### 3. Render from the file

```bash
node ~/figma-cli/src/index.js render "$(cat path/to/screen.jsx)" --keep-wrapper
```

Capture the returned node ID. Use `--keep-wrapper` for a composed screen or
component whose outer frame must remain intact. Without it, the renderer may
intentionally split a layout-only wrapper around same-named children into
independent top-level nodes.

When the JSX uses `var:` colors, pin resolution to the project's collection:

```bash
node ~/figma-cli/src/index.js render "$(cat path/to/screen.jsx)" \
  --keep-wrapper -c "<collection>"
```

Find the collection from the project or list variables; never guess it.

### 4. Verify visually

```bash
node ~/figma-cli/src/index.js verify "<node-id>" \
  --save path/to/previews/screen.png --scale 0.6
```

Open and inspect the PNG. Saving it is not verification by itself. Check at
least: clipping, wrapping, hierarchy, alignment, spacing, colors, icons, and
whether the top-level frame landed without covering existing work. Fix the JSX,
re-render, and inspect again when anything is wrong.

Keep generated node IDs only in project documentation or output where they are
useful for the current Figma file. Do not treat them as stable identifiers.

### 5. Arrange without disturbing existing work

New renders can overlap. Inspect nearby top-level nodes before moving anything.
Prefer `unstack` for overlap repair or targeted `set`/`set-batch` coordinates.
`arrange` sorts and moves all top-level frames, so use it only when the user
wants the whole canvas rearranged. Do not delete or replace existing nodes
unless the user explicitly requests it and the target IDs have been verified.

## Silent failure traps

- Multi-word text needs `w="fill"` on the `Text` and a width-bearing/filling
  parent or it can clip to one line.
- DSL props are not CSS props. Use `flex`, `p`, `bg`, `rounded`, `size`, and
  `weight` rather than `layout`, `padding`, `fill`, `cornerRadius`, `fontSize`,
  or `fontWeight`.
- `var:` binds color-like properties. Numeric layout values such as padding,
  gap, radius, and text size remain numeric literals; resolve the token value
  first instead of writing `rounded="var:md"`.
- Pass `-c <collection>` whenever unqualified `var:` names could resolve against
  more than one collection.
- Use a growing spacer frame instead of relying on `justify="between"` for
  edge-separated content.
- Center button contents with `flex="row" justify="center" items="center"`.
- Use `<Icon name="lucide:..." />` rather than emojis, whose rendering varies.
- A request for N movable items usually means N top-level nodes. Do not bundle
  them under one wrapper unless the requested artifact is a composed set.
- After a render, trust the screenshot over a successful exit code.

## Tokens and DESIGN.md

Use a project `DESIGN.md` as the documented token source when one exists:

```bash
node ~/figma-cli/src/index.js import path/to/DESIGN.md -c "<collection>"
node ~/figma-cli/src/index.js var visualize "<collection>"
```

Inspect existing collections and variable names before importing or creating
new ones. Preserve semantic naming and avoid creating a near-duplicate token
because a lookup was skipped. Re-render token-bound sources with the same
collection and verify them after an import.

## Optional project organization

If the repository has no convention, this layout keeps a flow reproducible:

```text
designs/<flow>/
  desktop/
    01-*.jsx
    previews/
  mobile/
    01-*.jsx
    previews/
  DESIGN.md
  README.md
```

Treat it as a default, not a universal rule. Create only the requested
viewports. Record screen order, dimensions, collection name, render commands,
and current node IDs in the flow README when that context will help the next
edit.

## HTML conversion

Only create an HTML counterpart when the user requests one or the project
already maintains HTML previews. Translate the DSL's hierarchy and auto-layout
to semantic HTML/flexbox, preserve dimensions and tokens, and follow the
project's existing dependency policy. Do not automatically add Google Fonts or
CDN scripts to an offline or dependency-constrained project.

## Completion checklist

- The source file lives in the project and follows neighboring conventions.
- The CLI connected to the intended active Figma file.
- Token-bound renders used the intended collection.
- The result was rendered with the correct wrapper behavior.
- A preview was saved and visually inspected.
- Clipping, layout, tokens, and icons were corrected after inspection.
- Existing canvas work was not deleted or globally rearranged without consent.
- The user receives the changed source paths, resulting node IDs when useful,
  and preview paths.
