#!/bin/bash
# May also be launched with: zsh install_mac.sh
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
. "$SCRIPT_DIR/common.sh"
require_mac
xcode-select -p >/dev/null 2>&1 || fail 'Run xcode-select --install, complete Apple’s installer, then rerun.'
command -v git >/dev/null 2>&1 || fail 'Install Apple Command Line Tools: xcode-select --install'
mkdir -p "$ARIA_ROOT"
# Refuse to repurpose any existing checkout; the older package remains intact.
UPSTREAM_SHA=9b294b3d0536135442ea73cb01e6cb3ca7029dd3
ARIA_UPSTREAM="$ARIA_ROOT/LivePortrait-$UPSTREAM_SHA"
if [ ! -e "$ARIA_UPSTREAM" ]; then
  git clone https://github.com/KlingAIResearch/LivePortrait.git "$ARIA_UPSTREAM"
fi
[ -d "$ARIA_UPSTREAM/.git" ] || fail "Not a Git checkout: $ARIA_UPSTREAM"
[ -z "$(git -C "$ARIA_UPSTREAM" status --porcelain --untracked-files=no)" ] || fail "Uncommitted upstream changes: $ARIA_UPSTREAM . Preserve them before continuing."
if [ "$(git -C "$ARIA_UPSTREAM" rev-parse HEAD)" != "$UPSTREAM_SHA" ]; then
  git -C "$ARIA_UPSTREAM" checkout --detach "$UPSTREAM_SHA"
fi
if [ ! -d "$ARIA_ENV/conda-meta" ]; then
  conda create -y -p "$ARIA_ENV" --override-channels -c conda-forge python=3.10 pip ffmpeg
fi
# conda run avoids shell initialization and accidentally using base-environment pip.
run_env python -c 'import platform,sys; assert platform.machine()=="arm64", "Environment must be arm64"; assert sys.version_info[:2]==(3,10), "Python 3.10 required"'
run_env python -m pip install -r "$SCRIPT_DIR/requirements-apple-silicon.txt"
run_env python -m pip check
run_env python "$SCRIPT_DIR/aria_runtime.py" prepare --root "$ARIA_ROOT"
PYTORCH_ENABLE_MPS_FALLBACK=1 run_env python "$SCRIPT_DIR/aria_runtime.py" doctor --root "$ARIA_ROOT"
echo "Environment checks passed. Animation is NOT verified until an ARIA render passes and is visually reviewed."
echo "Next: zsh \"$SCRIPT_DIR/animate_aria.sh\" /absolute/path/to/driving.mp4"

