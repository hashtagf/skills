# Running Kimi K3 as an agent (Kimi Code CLI @ kimi-k3)

The `kimi-k3` skill's runner is a **stateless, tool-less** one-shot API call — great for a
single prompt, a review, or a self-contained artifact, but it can't read a repo, edit files,
run tests, or iterate. To use Kimi K3 as a real **agentic implementer** (its own tool loop),
run it through Moonshot's own **Kimi Code CLI** pinned to the `kimi-k3` model. This is the
harness Kimi is tuned for, so it's the best shot at K3's true coding ceiling — no hand-rolled
agent loop required. The `kimi-k3-implement` subagent drives this; this file is its setup +
reference.

> The docs advertise only the k2 family, but the CLI does **not** allowlist model names
> (the `moonshot-ai` platform accepts the `kimi-k` prefix), so `kimi-k3` works when configured
> explicitly — verified to do real agentic tool-use.

## 1. Install the CLI

```bash
uv tool install kimi-cli      # recommended (isolated); or: pip install kimi-cli
```

Binaries `kimi` / `kimi-cli` land on your PATH (e.g. `~/.local/bin/kimi`).

## 2. Configure it for kimi-k3

Kimi CLI reads `~/.kimi/config.toml`. Create it with a `kimi-k3` model pointed at the
Moonshot endpoint:

```toml
default_model = "kimi-k3"

[providers.moonshot]
type = "kimi"
base_url = "https://api.moonshot.ai/v1"
api_key = "sk-REPLACE_WITH_YOUR_MOONSHOT_KEY"

[models.kimi-k3]
provider = "moonshot"
model = "kimi-k3"
max_context_size = 1048576
```

**Fast path:** the skill bundles a helper that writes this file for you —
`skills/kimi-k3/scripts/setup.sh --with-cli sk-your-key` (merges into any existing
`~/.kimi/config.toml`, sets `default_model = "kimi-k3"`, chmod 600). It's user-run; an agent
should never run it with a scavenged key.

**Credentials — pick one, don't commit the key:**
- run `scripts/setup.sh --with-cli sk-...` (above), **or**
- put your key directly in `api_key` above (this file is local to your machine — never commit it), **or**
- run `kimi` once interactively and use `/login` to store credentials in `~/.kimi/`.

`~/.kimi/config.toml` and `~/.kimi/` are user-local; keep them out of version control.
`max_context_size` is required by the CLI (`1048576` = K3's 1M window).

## 3. Verify

```bash
kimi --print --quiet -m kimi-k3 -p "Reply with exactly one word: PONG"   # expect: PONG
```

If you get `LLM not set`, the config's model/provider isn't resolving — re-check step 2.

## Headless flags this subagent uses

| Flag | Meaning |
|---|---|
| `--print` | Non-interactive: run once and exit (no TUI). |
| `-p, --prompt TEXT` | The task to hand K3. |
| `-y, --yolo` | Auto-approve all tool calls (needed for unattended runs). |
| `-m kimi-k3` | Force the model. |
| `-w, --work-dir DIR` | Restrict the agent's workspace to DIR. |
| `--quiet` | Print only the final message (clean stdout). |

## Safety

`--yolo` lets K3 edit files and run shell commands **unsupervised**. Always:
- point `-w` at the specific directory it should touch, and
- run inside a **git repo** (or a throwaway/worktree) so every change shows up in `git diff`
  and is trivially reversible (`git checkout -- .`) before anything is committed.

Never let it run `--yolo` against an untracked or precious directory.
