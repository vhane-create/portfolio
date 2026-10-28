#!/bin/bash
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
. "$SCRIPT_DIR/common.sh"
require_mac
[ -d "$ARIA_ENV/conda-meta" ] || fail 'Run zsh install_mac.sh first.'
run_env python -m pip check
PYTORCH_ENABLE_MPS_FALLBACK=1 run_env python "$SCRIPT_DIR/aria_runtime.py" doctor --root "$ARIA_ROOT"
