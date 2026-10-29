#!/bin/bash
set -euo pipefail
ARIA_DEMO_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is needed. Use the Python installation from your existing ARIA setup."
  read -r -p "Press Return to close. "
  exit 1
fi
ARIA_RUNTIME_ROOT="${ARIA_ROOT:-$HOME/ARIA-LivePortrait}"
ARIA_HEART_PYTHON="$ARIA_RUNTIME_ROOT/env-heart/bin/python"
if [ -x "$ARIA_HEART_PYTHON" ]; then
  exec "$ARIA_HEART_PYTHON" "$ARIA_DEMO_DIR/server.py"
fi
exec python3 "$ARIA_DEMO_DIR/server.py"
