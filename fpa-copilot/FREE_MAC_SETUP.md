# ARIA — free Mac development setup

This is the no-subscription development track. It does **not** claim that ARIA's photorealistic real-time avatar is complete.

## First: test the existing browser-based ARIA

1. Open https://vhane-create.github.io/portfolio/fpa-copilot/aria.html in Chrome.
2. Allow microphone access if prompted.
3. Try the browser's speech controls and test questions. Browser speech synthesis/recognition availability varies.
4. The live AI backend requires separate deployment and configuration. Without it, use the existing prototype features only.

## Local website preview (Apple Silicon Mac)

Open **Terminal** and run:

```bash
git clone https://github.com/vhane-create/portfolio.git
cd portfolio
python3 -m http.server 8000
```

Then open http://localhost:8000/fpa-copilot/aria.html in Chrome. If you already cloned the repository, enter that folder and use `git pull` instead of cloning again. Stop the server with Control-C.

## Portrait asset needed

The approved ARIA portrait must be saved as `fpa-copilot/aria-portrait.webp` in the repository. The website cannot display the image until that binary asset is uploaded. Do not replace it with a generic robot.

## Realistic lip-sync: experimental, not yet verified on this Mac

LiveTalking: https://github.com/lipku/LiveTalking

The upstream quick start uses Linux, NVIDIA CUDA and model weights. Apple Silicon does not support CUDA, and installing the CUDA-specific commands on an M4 Mac will not work. Do **not** run the upstream CUDA PyTorch install command on macOS.

Mac compatibility, memory use, rendering speed and the user's custom-avatar preparation all require hands-on testing before adopting this path. Do not publish a GPU-dependent service as a functioning GitHub Pages-only app: GitHub Pages hosts static content, not an inference server.

## Free-first release criteria

- Approved portrait displays reliably.
- Two-way voice works in a supported browser.
- Lip movement is visibly synchronized with generated speech, not merely a timed CSS loop.
- Company claims have sources and financial responses distinguish sample data.
- No private keys are committed to GitHub.
- A public visitor can use the demo without manually pasting a provider URL.

