# Shared by the plain-text launch scripts; compatible with bash and zsh.
set -eu
ARIA_SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ARIA_ROOT="${ARIA_ROOT:-$HOME/ARIA-LivePortrait}"
ARIA_ENV="$ARIA_ROOT/env-apple-silicon"
fail() { echo "ERROR: $*" >&2; exit 1; }
require_mac() {
  [ "$(uname -s)" = Darwin ] && [ "$(uname -m)" = arm64 ] || fail 'Use native Apple Silicon macOS Terminal (turn off Open using Rosetta for Terminal if enabled).'
  command -v conda >/dev/null 2>&1 || fail 'Install Apple Silicon Miniforge: https://github.com/conda-forge/miniforge . Reopen Terminal, then rerun.'
}
run_env() { conda run --no-capture-output -p "$ARIA_ENV" "$@"; }

