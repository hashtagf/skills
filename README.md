# hashtagf-skills

Skill warehouse for hashtagf — a collection of reusable [Claude Code agent skills](https://docs.claude.com/en/docs/claude-code/skills), installable as a Claude Code plugin or via the `skills` CLI.

## Skills

| Skill | Description |
|---|---|
| [design-system-builder](skills/design-system-builder/SKILL.md) | Build, extract, or repair a complete design system (tokens + components + states + docs). Three modes: CREATE, EXTRACT, REDESIGN. |
| [kimi-k3](skills/kimi-k3/SKILL.md) | Send a prompt to Moonshot's Kimi K3 model (1M context, vision, thinking mode) via a bundled runner script and relay its answer. For second opinions, cross-model checks, long-context reads. Needs `MOONSHOT_API_KEY`. |

## Agents

Subagents bundled with the plugin (auto-discovered from `agents/`). Invoke via the Agent tool (`subagent_type`) or by name.

| Agent | Description |
|---|---|
| [kimi-k3](agents/kimi-k3.md) | Thin Haiku-powered orchestrator that delegates a whole subtask to Kimi K3 (via the `kimi-k3` skill's runner) in an isolated context and relays the answer. Use to hand off a prompt / second opinion / vision question to Kimi K3 without cluttering the main thread. Needs `MOONSHOT_API_KEY`. |

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
agents/
└── <agent-name>.md  # Bundled subagent (YAML frontmatter + system prompt)
```

Skills under `skills/` are auto-discovered by both the plugin system and the skills CLI.
Subagents under `agents/` are auto-discovered by the plugin system (lowest precedence — a
project `.claude/agents/<name>.md` with the same name overrides them).

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with `name` + `description` frontmatter.
2. Add it to the table above.
3. Bump `version` in `.claude-plugin/plugin.json` and `marketplace.json`.
4. Verify: `claude plugin validate .`

## Development

Skills are created and iterated with the `skill-creator` skill. `*-workspace/` directories are local iteration scratch (fixtures, eval runs) and are not committed.
