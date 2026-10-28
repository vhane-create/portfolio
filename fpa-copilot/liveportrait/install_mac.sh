#!/bin/zsh
set -e
echo "ARIA LivePortrait setup — Apple Silicon"
if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then echo "Requires Apple Silicon macOS"; exit 1; fi
if ! command -v git >/dev/null; then echo "Install Apple's Command Line Tools: xcode-select --install"; exit 1; fi
if ! command -v conda >/dev/null; then echo "Conda is needed. Install Miniforge from https://github.com/conda-forge/miniforge then rerun."; exit 1; fi
if ! command -v ffmpeg >/dev/null; then echo "FFmpeg is needed. Install with 'brew install ffmpeg' or 'conda install -c conda-forge ffmpeg' then rerun."; exit 1; fi
ROOT="$HOME/ARIA-LivePortrait"
mkdir -p "$ROOT"
cd "$ROOT"
if [[ ! -d LivePortrait/.git ]]; then git clone https://github.com/KlingAIResearch/LivePortrait.git; fi
cd LivePortrait
eval "$(conda shell.zsh hook)"
if ! conda env list | awk '{print $1}' | grep -qx aria-liveportrait; then conda create -y -n aria-liveportrait python=3.10; fi
conda activate aria-liveportrait
python -m pip install -r requirements_macOS.txt
python -m pip install "huggingface_hub[cli]"
if command -v hf >/dev/null; then hf download KlingTeam/LivePortrait --local-dir pretrained_weights --exclude "*.git*" "README.md" "docs"; else huggingface-cli download KlingTeam/LivePortrait --local-dir pretrained_weights --exclude "*.git*" "README.md" "docs"; fi
echo ""
echo "Setup finished. Put your approved portrait at $ROOT/aria-approved.png"
echo "Then run the ARIA animation script with a driving video."
