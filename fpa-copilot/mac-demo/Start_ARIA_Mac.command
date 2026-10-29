#!/bin/bash
set -euo pipefail
ARIA_DEMO_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is needed. Use the Python installation from your existing ARIA setup."
  read -r -p "Press Return to close. "
  exit 1
fi
python3 "$ARIA_DEMO_DIR/server.py"
