# ARIA — LivePortrait setup (Apple Silicon Mac)
This folder connects the approved ARIA business-suit portrait to the open-source [KlingAIResearch/LivePortrait](https://github.com/KlingAIResearch/LivePortrait) project. LivePortrait is not copied or claimed as our own; install it from its upstream repository and follow its license.

## Get started on MacBook M4
1. Install [Homebrew](https://brew.sh/) and Miniforge (or another compatible Conda distribution).
2. In Terminal, run:
   ```bash
   git clone https://github.com/KlingAIResearch/LivePortrait.git
   cd LivePortrait
   ```
3. Follow the **Apple Silicon / macOS** section in the upstream README for its current environment, dependencies, and model-weight downloads. Do not assume CUDA instructions work on a Mac.
4. Copy your **approved** ARIA portrait to the input directory specified by LivePortrait.
5. Supply a driving video with clear, naturally spoken facial motion, then run the upstream inference command documented for macOS.
6. Preview the resulting MP4. Keep the original portrait unchanged.

## Important
- A portrait + driving video produces an animated **video**, not an interactive 3D model or a live conversational assistant.
- This repo contains integration instructions only. The upstream AI weights and dependencies are **not installed on GitHub Pages**, and GitHub Pages cannot run Python AI inference.
- Only use driving videos and voices you have permission to use.
- To show the final result in the ARIA portfolio, upload the generated MP4 into `fpa-copilot/` and link it from the existing ARIA page.

Source: https://github.com/KlingAIResearch/LivePortrait
