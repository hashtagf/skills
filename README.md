# hashtagf-skills

Skill warehouse for hashtagf — a collection of reusable [Claude Code agent skills](https://docs.claude.com/en/docs/claude-code/skills), installable as a Claude Code plugin or via the `skills` CLI.

## Skills

| Skill | Description |
|---|---|
| [design-system-builder](skills/design-system-builder/SKILL.md) | Build, extract, or repair a complete design system (tokens + components + states + docs). Three modes: CREATE, EXTRACT, REDESIGN. |

## Install

### As a Claude Code plugin (recommended)

```
/plugin marketplace add hashtagf/skills
/plugin install hashtagf-skills@hashtagf
```

Or test locally before pushing to GitHub:

```
/plugin marketplace add /path/to/hashtagf-skills
/plugin install hashtagf-skills@hashtagf
```

### Via the skills CLI (npx)

```bash
npx skills add hashtagf/skills          # install all skills
npx skills add hashtagf/skills --skill design-system-builder
```

### Manual copy

```bash
cp -r skills/design-system-builder ~/.claude/skills/        # personal (all projects)
cp -r skills/design-system-builder <project>/.claude/skills/ # project-scoped
```

Then invoke with `/design-system-builder` or let it trigger automatically from a matching request.

## Structure

```
.claude-plugin/
├── plugin.json       # Plugin manifest (name, version, author)
└── marketplace.json  # Marketplace manifest (lists this repo's plugins)
skills/
└── <skill-name>/
    ├── SKILL.md      # Skill definition and instructions
    ├── references/   # Supporting reference docs loaded on demand
    └── evals/        # Eval cases for testing the skill
```

Skills under `skills/` are auto-discovered by both the plugin system and the skills CLI.

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with `name` + `description` frontmatter.
2. Add it to the table above.
3. Bump `version` in `.claude-plugin/plugin.json` and `marketplace.json`.
4. Verify: `claude plugin validate .`

## Development

Skills are created and iterated with the `skill-creator` skill. `*-workspace/` directories are local iteration scratch (fixtures, eval runs) and are not committed.
