#!/bin/bash
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
. "$SCRIPT_DIR/common.sh"
require_mac
[ "$#" -le 1 ] || fail 'Usage: zsh animate_aria.sh /absolute/path/to/driving.mp4'
[ -d "$ARIA_ENV/conda-meta" ] || fail 'Run zsh install_mac.sh first.'
PYTORCH_ENABLE_MPS_FALLBACK=1 run_env python "$SCRIPT_DIR/aria_runtime.py" animate --root "$ARIA_ROOT" --driving "${1:-$ARIA_ROOT/driving.mp4}"
