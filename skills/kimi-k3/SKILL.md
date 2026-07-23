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

Delegate a prompt to **Kimi K3** (Moonshot) and relay its reply. K3 is a 2.8T-parameter
model: 1M-token context, native vision, thinking mode on by default (`reasoning_effort`
low/high/max, default max), OpenAI chat-completions protocol.

Use when the user explicitly wants Kimi K3 in the loop — second opinion, cross-check,
long-context read, image question — not as a replacement for your own help.

## Prerequisite: API key

The runner reads `MOONSHOT_API_KEY` from the environment. If it's **not** set, don't hunt
through shell dotfiles (`~/.zshrc`, `~/.zprofile`, …) — that's fragile and trips security
tooling. Ask the user to set it:

```bash
# this session only:
export MOONSHOT_API_KEY=sk-...

# persist for ALL shells (non-interactive ones too — ~/.zshrc is NOT loaded there,
# so a key set only there won't reach the runner; ~/.zshenv is):
echo 'export MOONSHOT_API_KEY=sk-...' >> ~/.zshenv
```

Or point them to the bundled one-time helper (**user-run**): `scripts/setup.sh sk-...`
persists the key to `~/.zshenv`; add `--with-cli` to also configure the Kimi CLI for the
`kimi-k3-implement` agent. Don't run it yourself, and never pass it a key you found on the
system — handing over a key is the user's call.

Get a key at https://platform.moonshot.ai (min $1 top-up unlocks the model). Never hardcode
or invent a key.

## How to run

Call the runner (`scripts/kimi_k3.py` beside this file) by its **absolute path** — the
working directory usually isn't the skill directory. Pure Python stdlib: no `pip`, `jq`,
or `curl` escaping.

```bash
KIMI="/absolute/path/to/kimi-k3/scripts/kimi_k3.py"   # e.g. .../.claude/skills/kimi-k3/scripts/kimi_k3.py

python3 "$KIMI" "Explain lock-free queues in 3 bullets"
cat report.md | python3 "$KIMI" "Summarize the risks in this doc"
python3 "$KIMI" --system "You are a terse Rust reviewer" --effort high "review: <code>"
python3 "$KIMI" --image ./architecture.png "What does this design do?"
```

Prefer **stdin** for long prompts or anything with quotes/backticks/newlines. Pass the
user's content faithfully — don't paraphrase it into the call.

### Flags

| Flag | Purpose |
|---|---|
| `--system TEXT` | System prompt / role. |
| `--effort low\|high\|max` | Reasoning depth. Omit for model default (max); use `low` for quick factual asks. |
| `--image PATH\|URL` | Attach an image (repeatable). Local path is base64-inlined; URL passed through. |
| `--show-reasoning` | Also print Kimi's thinking trace before the answer. |
| `--model NAME` | Override the model id (default `kimi-k3`). |
| `--temperature`, `--max-tokens` | Standard sampling controls. |
| `--json` | Print the raw API response (for scripting / debugging). |
| `--base-url URL` | Override the endpoint (default `https://api.moonshot.ai/v1`, or `$MOONSHOT_BASE_URL`). |
| `--timeout SECS` | Request timeout (default 300). |

Token usage prints to stderr after each call, so captured stdout stays clean.

## Relaying the answer

Give the user Kimi K3's response, clearly attributed ("Kimi K3 says:") as another model's
output, not your own conclusion. For a comparison or second opinion, add your own brief
take alongside.

## When it fails

The script exits non-zero with a one-line reason on stderr:
- **`MOONSHOT_API_KEY is not set`** → ask the user to export it (see Prerequisite); suggest `~/.zshenv` so non-interactive shells pick it up. Don't hunt dotfiles.
- **`API error 401`** → key is wrong/expired.
- **`API error 429` / insufficient balance** → account needs a top-up (min $1 unlocks access).
- **`network error`** → connectivity/endpoint issue; retry or check `--base-url`.

Report the failure plainly — never retry blindly or fabricate a Kimi response.
