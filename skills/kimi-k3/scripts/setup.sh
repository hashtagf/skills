#!/usr/bin/env bash
# One-time setup helper for the kimi-k3 skill — USER-INVOKED ONLY.
#
# Persists MOONSHOT_API_KEY where the runner (and non-interactive shells) can see it,
# and optionally configures Moonshot's Kimi CLI to use the kimi-k3 model. This exists
# because a key set only in ~/.zshrc never reaches non-interactive shells (which is how
# tools/scripts run) — ~/.zshenv does.
#
# You provide the key EXPLICITLY — this script never searches your system for one:
#   scripts/setup.sh sk-your-key
#   MOONSHOT_API_KEY=sk-your-key scripts/setup.sh
#   scripts/setup.sh                 # prompts, hidden input
#
# Flags:
#   --with-cli   also write ~/.kimi/config.toml so the kimi-k3-implement agent can run
#   -h, --help   show this help
#
# NOTE FOR AI AGENTS: do NOT run this on the user's behalf, and NEVER pass it a key you
# discovered on the system (env dumps, dotfiles, history, etc.). Writing a secret into a
# user's shell config is the user's decision to make, with a key they chose to hand over.
set -euo pipefail

WITH_CLI=0
KEY_ARG=""
for a in "$@"; do
  case "$a" in
    --with-cli) WITH_CLI=1 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "unknown flag: $a" >&2; exit 2 ;;
    *) KEY_ARG="$a" ;;
  esac
done

# Resolve the key explicitly: arg > env > interactive prompt. Never scavenge.
KEY="${KEY_ARG:-${MOONSHOT_API_KEY:-}}"
if [ -z "$KEY" ]; then
  printf 'Paste your MOONSHOT_API_KEY (input hidden): ' >&2
  read -rs KEY; echo >&2
fi
[ -n "$KEY" ] || { echo "setup: no key provided" >&2; exit 2; }
case "$KEY" in
  sk-*) : ;;
  *) echo "setup: warning — key doesn't start with 'sk-'; continuing anyway." >&2 ;;
esac

redact() { printf '%s' "sk-***${1: -4}"; }   # show only last 4 chars

# 1) Persist to ~/.zshenv (idempotent: replace an existing export, else append).
ZE="$HOME/.zshenv"
touch "$ZE"
LINE="export MOONSHOT_API_KEY='$KEY'"
if grep -q '^export MOONSHOT_API_KEY=' "$ZE" 2>/dev/null; then
  tmp="$(mktemp)"; grep -v '^export MOONSHOT_API_KEY=' "$ZE" > "$tmp" || true
  printf '%s\n' "$LINE" >> "$tmp"; mv "$tmp" "$ZE"
  echo "updated MOONSHOT_API_KEY in $ZE"
else
  printf '\n# Moonshot / Kimi K3 API key (added by kimi-k3 skill setup)\n%s\n' "$LINE" >> "$ZE"
  echo "added MOONSHOT_API_KEY to $ZE"
fi
chmod 600 "$ZE"
echo "  -> $(redact "$KEY")  (perms 600)"

# 2) Optional: configure Kimi Code CLI for kimi-k3 (merge, don't clobber).
if [ "$WITH_CLI" -eq 1 ]; then
  KC="$HOME/.kimi/config.toml"
  mkdir -p "$HOME/.kimi"
  if [ -f "$KC" ] && grep -q 'models.kimi-k3' "$KC" 2>/dev/null; then
    echo "$KC already defines kimi-k3 — leaving it unchanged."
  else
    if [ -f "$KC" ]; then
      cp "$KC" "$KC.bak.$(date +%s)"
      if grep -q '^default_model' "$KC"; then
        sed -i.tmp 's/^default_model = .*/default_model = "kimi-k3"/' "$KC"; rm -f "$KC.tmp"
      else
        printf 'default_model = "kimi-k3"\n' | cat - "$KC" > "$KC.new" && mv "$KC.new" "$KC"
      fi
    else
      printf 'default_model = "kimi-k3"\n' > "$KC"
    fi
    cat >> "$KC" <<EOF

[providers.moonshot]
type = "kimi"
base_url = "https://api.moonshot.ai/v1"
api_key = "$KEY"

[models.kimi-k3]
provider = "moonshot"
model = "kimi-k3"
max_context_size = 1048576
EOF
    chmod 600 "$KC"
    echo "configured Kimi CLI for kimi-k3 in $KC (perms 600)"
  fi
fi

echo
echo "Done. Open a new terminal (or: source ~/.zshenv) so the key loads, then verify:"
echo "  python3 \"\$(dirname \"\$0\")/kimi_k3.py\" --effort low 'Reply with the single word READY'"
[ "$WITH_CLI" -eq 1 ] && echo "  kimi --print -m kimi-k3 -p 'Reply with the single word READY'"
