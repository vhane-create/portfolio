#!/bin/zsh
set -e
ROOT="$HOME/ARIA-LivePortrait"
IMAGE="$ROOT/aria-approved.png"
DRIVER="${1:-$ROOT/driving.mp4}"
if [[ ! -f "$IMAGE" ]]; then echo "Missing approved ARIA image: $IMAGE"; exit 1; fi
if [[ ! -f "$DRIVER" ]]; then echo "Missing driving video: $DRIVER"; exit 1; fi
cd "$ROOT/LivePortrait"
eval "$(conda shell.zsh hook)"
conda activate aria-liveportrait
PYTORCH_ENABLE_MPS_FALLBACK=1 python inference.py -s "$IMAGE" -d "$DRIVER" --flag_crop_driving_video
echo "Done. Look in $ROOT/LivePortrait/animations for the MP4."
