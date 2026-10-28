#!/bin/zsh
set -eu
ARIA_PROJECT="$(cd "$(dirname "$0")" && pwd)"
export ARIA_PROJECT
export ARIA_ROOT="${ARIA_ROOT:-$HOME/ARIA-LivePortrait}"
voice_python="$ARIA_ROOT/env-heart/bin/python"
if [[ ! -x "$voice_python" ]]; then
  print "Voice environment missing. Follow README.md, or run setup_runtime.py first."
  exit 1
fi
exec "$voice_python" "$ARIA_PROJECT/heart-backend/heart_server.py"
