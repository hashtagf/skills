#!/usr/bin/env bash
# Install the `remote-test` CLI from this skill (macOS/Linux).
#   bash scripts/install.sh /path/to/team.json
# team.json comes from your queue admin: {"api_url": "...", "bucket": "...", "project": "..."}
# Re-run to upgrade. Requires python3 >= 3.9, git, gcloud (signed in with your company account).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HOME/.local/share/remote-test/lib"
BIN="$HOME/.local/bin"
CONF="$HOME/.config/remote-test"

for tool in python3 git gcloud; do
  command -v "$tool" >/dev/null || { echo "missing: $tool (gcloud: https://cloud.google.com/sdk/docs/install)"; exit 1; }
done
python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' || { echo "python3 >= 3.9 required"; exit 1; }

mkdir -p "$LIB" "$BIN" "$CONF"
if [ -n "${1:-}" ]; then
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert {"api_url","bucket"} <= set(d), "team.json needs api_url and bucket"' "$1"
  install -m 600 "$1" "$CONF/team.json"
elif [ ! -f "$CONF/team.json" ]; then
  echo "usage: install.sh /path/to/team.json  (ask your queue admin for this file)"; exit 2
fi
install -m 644 "$HERE"/client.py "$HERE"/core.py "$HERE"/gcp.py "$LIB"/

launcher="$BIN/remote-test"
if [ -e "$launcher" ] && ! grep -q 'remote-test/lib/client.py' "$launcher" 2>/dev/null; then
  mv "$launcher" "$launcher.before-$(date +%Y%m%d-%H%M%S)"; echo "kept previous launcher next to $launcher"
fi
printf '#!/bin/sh\nexec python3 "%s/client.py" "$@"\n' "$LIB" > "$launcher"; chmod 755 "$launcher"

case ":$PATH:" in *":$BIN:"*) ;; *) echo "NOTE: add $BIN to PATH";; esac
echo "Checking access..."
if "$launcher" whoami; then echo "Installed. Next: remote-test setup (inside a repo)"
else echo "Installed, but access failed: run 'gcloud auth login'; a 403 means you are not in the team's access group."; fi
