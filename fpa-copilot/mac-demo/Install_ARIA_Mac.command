#!/bin/bash
set -euo pipefail
ARIA_INSTALLER_DIR="$(cd "$(dirname "$0")" && pwd)"
ARIA_RUNTIME_ROOT="${ARIA_ROOT:-$HOME/ARIA-LivePortrait}"
if [ -x "$ARIA_RUNTIME_ROOT/env-heart/bin/python" ]; then
  exec "$ARIA_RUNTIME_ROOT/env-heart/bin/python" "$ARIA_INSTALLER_DIR/installer/install_mac.py"
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is needed. Use the Python installation from your previous ARIA setup."
  read -r -p "Press Return to close. "
  exit 1
fi
python3 "$ARIA_INSTALLER_DIR/installer/install_mac.py"
