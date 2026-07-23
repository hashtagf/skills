---
name: kimi-k3
description: >-
  Send a prompt to Moonshot's Kimi K3 model and relay its answer, using the bundled
  runner script. Use this skill whenever the user wants to ask, query, run, or delegate
  something to Kimi K3 / Kimi / the Moonshot model — e.g. "ask kimi-k3 to…", "get a second
  opinion from kimi", "run this through kimi k3", "ให้ kimi ช่วยดู…" — or wants another
  model's take on a question, code review, or reasoning problem, or to use Kimi K3's 1M
  context / vision / thinking mode. Do NOT use it to write Kimi/Moonshot integration code
  into the user's own app — that's a normal coding task, not this skill.
---

# Kimi K3

Delegate a prompt to **Kimi K3** (Moonshot) and bring its reply back to the user. Kimi K3
is a 2.8T-parameter model with a 1M-token context window, native vision, and thinking mode
on by default (`reasoning_effort`: low/high/max, default max). It speaks the OpenAI
chat-completions protocol.

Reach for this when the user explicitly wants Kimi K3 in the loop — a second opinion, a
cross-check against another model, a long-context read, or an image question — not as a
replacement for your own direct help.

## Prerequisite: API key

The runner reads `MOONSHOT_API_KEY` from the environment. If it's set, you're ready.

If it's **not** set, do not go rummaging through the user's shell dotfiles (`~/.zshrc`,
`~/.zprofile`, …) to find it — auto-hunting for a credential across profile files is fragile
and trips security tooling. Instead, ask the user to make the key available, and point out
the durable fix:

```bash
# just this session:
export MOONSHOT_API_KEY=sk-...

# persist for ALL shells, including the non-interactive ones that tools/scripts run in
# (note: ~/.zshrc is NOT loaded by non-interactive shells, which is why a key set only there
#  won't reach the runner — ~/.zshenv is):
echo 'export MOONSHOT_API_KEY=sk-...' >> ~/.zshenv
```

Get a key at https://platform.moonshot.ai (a min $1 top-up unlocks the model). Never hardcode
or invent a key.

## How to run it

The runner lives at `scripts/kimi_k3.py` next to this file. Call it by its **absolute path** —
the working directory usually isn't the skill directory, so a relative path won't resolve.
Set it once to the `scripts/kimi_k3.py` beside this SKILL.md:

```bash
KIMI="/absolute/path/to/kimi-k3/scripts/kimi_k3.py"   # e.g. .../.claude/skills/kimi-k3/scripts/kimi_k3.py
```

It's pure Python stdlib — no `pip install`, no `jq`, no `curl` escaping.

```bash
# simplest — prompt as an argument
python3 "$KIMI" "Explain lock-free queues in 3 bullets"

# long or multi-line prompts: pipe via stdin so quoting never bites you
cat report.md | python3 "$KIMI" "Summarize the risks in this doc"

# steer it
python3 "$KIMI" --system "You are a terse Rust reviewer" --effort high "review: <code>"

# ask about an image (local path is base64-inlined; a URL is passed through)
python3 "$KIMI" --image ./architecture.png "What does this design do?"
```

Prefer **stdin** for anything long or containing quotes/backticks/newlines — it sidesteps
shell-escaping entirely. Pass the user's actual content faithfully; don't paraphrase their
prompt into the call.

### Useful flags

| Flag | Purpose |
|---|---|
| `--system TEXT` | System prompt / role. |
| `--effort low\|high\|max` | Reasoning depth. Omit to use the model default (max). Drop to `low` for quick factual asks. |
| `--image PATH\|URL` | Attach an image (repeatable). |
| `--show-reasoning` | Also print Kimi's thinking trace before the answer. |
| `--model NAME` | Override the model id (default `kimi-k3`). |
| `--temperature`, `--max-tokens` | Standard sampling controls. |
| `--json` | Print the raw API response (for scripting / debugging). |

Token usage is printed to stderr after each call so it doesn't pollute captured output.

## Relaying the answer

Run the script, then give the user Kimi K3's response. Attribute it clearly ("Kimi K3
says:") so it's obvious this is another model's output, not your own conclusion. If the
user asked for a comparison or second opinion, you can add your own brief take alongside it.

## When it fails

The script exits non-zero with a one-line reason on stderr:
- **`MOONSHOT_API_KEY is not set`** → ask the user to export it (see Prerequisite); suggest adding it to `~/.zshenv` so non-interactive shells pick it up. Don't hunt for it in their dotfiles.
- **`API error 401`** → key is wrong/expired.
- **`API error 429` / insufficient balance** → the account needs a top-up (min $1 unlocks access).
- **`network error`** → connectivity/endpoint issue; retry or check `--base-url`.

Report the failure plainly instead of retrying blindly or fabricating a Kimi response.
