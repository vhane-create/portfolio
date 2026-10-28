# ARIA LivePortrait — Apple Silicon Mac

This integration uses the **exact approved ARIA portrait** in `aria-approved.png`: long dark waves, black executive business suit, and subtle robotic details. The source PNG is preserved byte for byte. It is not regenerated, retouched, or replaced. SHA-256:

`9889d86d17f07437243204107a91ed7ab4a49a5a9d1841ec56c59d117247d958`

## Verification status

Code and portable workflow checks passed in a Linux workspace; **installation and animation on a MacBook Air M4 remain unverified**. No completed ARIA speaking video is supplied. The local doctor must pass, followed by a real driving-video render and visual review. See [VERIFICATION.md](VERIFICATION.md) for evidence and limitations.

## On your Mac: exact steps

Use the updated files in this repository, not the scripts in the earlier downloaded ZIP. Open **Terminal** or the VS Code terminal on your Mac; no remote access or administrator password needs to be sent to ChatGPT.

1. Install Apple's Command Line Tools if needed:
   ```sh
   xcode-select --install
   ```
   Complete the Apple installer. If tools are already installed, continue.
2. Install **Miniforge3-MacOSX-arm64** from the [official Miniforge release page](https://github.com/conda-forge/miniforge/releases). Follow its shell initialization instructions, close Terminal and reopen it. Check:
   ```sh
   uname -m
   conda --version
   ```
   `uname -m` must say `arm64`. If it says `x86_64`, use Terminal with “Open using Rosetta” unchecked. An Intel Conda installation cannot create this native environment; use arm64 Miniforge.
3. If you do not already have the portfolio repository locally:
   ```sh
   git clone https://github.com/vhane-create/portfolio.git "$HOME/portfolio"
   ```
   If it already exists, use its actual directory. Run `git status` first, preserve any local changes, then `git pull --ff-only`. Do not reset or overwrite local work.
4. Open the integration folder (adjust the path if your checkout is elsewhere):
   ```sh
   cd "$HOME/portfolio/fpa-copilot/liveportrait"
   cat install_mac.sh common.sh
   zsh install_mac.sh
   ```
   The installer creates `~/ARIA-LivePortrait/env-apple-silicon` with Python 3.10 and FFmpeg, downloads eight human model files, preserves ARIA's image, and runs verification. Internet access to GitHub, conda-forge, PyPI and Hugging Face is required. Allow several GB of free disk space. The environment is separate from the earlier named Conda environment and older LivePortrait folder.
5. Verification can be repeated at any time:
   ```sh
   zsh verify_mac.sh
   ```
   Success means native arm64 Python, PyTorch MPS, model loading, face detection and one neural frame passed. The report is `~/ARIA-LivePortrait/environment-check.json`; installed dependency versions are recorded in `installed-packages.txt`. It does **not** mean a speaking animation has passed.
6. Record a short **5–10 second** driving video with audio. Start facing forward with a neutral mouth, then speak the exact intended sentence, blink naturally once or twice, and make small nods/turns. Include a brief natural smile or open-mouth vowel so teeth can appear. Use one clearly visible, well-lit face, steady camera and minimal shoulder movement. Use your own permitted recording. A portrait and an audio file alone do not supply facial motion.
7. Render using the absolute path to that video:
   ```sh
   zsh animate_aria.sh "$HOME/Downloads/driving.mp4"
   ```
   Each run writes to a new folder under `~/ARIA-LivePortrait/animations/`. The script checks that the result contains video and audio and fully decodes it with FFmpeg. It prints the final ARIA MP4 path. Open it in QuickTime Player to review.

You may use another storage location by setting `ARIA_ROOT` to an absolute path for **all** three scripts, for example `ARIA_ROOT="$HOME/Movies/ARIA" zsh install_mac.sh`.

## Facial motion and appearance

The preset uses the full facial region, relative motion, stitching and pasteback to retain the original portrait, outfit and background outside the animated face. It uses a motion multiplier of 1.0, driving audio, and full precision. MPS fallback is enabled for unsupported GPU operations. CUDA, X-Pose/animals mode, and torch.compile are not used.

Blinking, lip motion and head movement come from the driving performance. The default experimental eye/lip retargeting switches remain off as recommended by upstream; normal expression transfer still animates those regions. No painted mouth, generic face or CSS teeth are added. Teeth are synthesized by the model when the mouth opens: their visibility, anatomy and stability **cannot be guaranteed**, especially from a closed-mouth source portrait. Review the actual output before claiming realism.

Use the same spoken audio as the driving performance. Browser text-to-speech of unrelated words will not synchronize with a prerecorded video. LivePortrait is a video-driven renderer; this integration does not turn GitHub Pages into a real-time audio-driven conversational avatar. An M4 Air may render slowly, and long videos consume more memory; start short.

## Visual acceptance checklist

- The face still looks like the approved ARIA, with the black suit, hair and robotic details preserved.
- Lip closures and openings line up with the audible syllables; teeth look stable during open-mouth frames.
- Blinks close and reopen both eyelids without flicker; small head motions look natural.
- No black frames, mouth smears, facial drift or obvious face/neck seams.
- Audio is present and the exported video plays completely.

A machine decode check does not assess these visual criteria. Keep the original source image unchanged even if a render needs a new driving performance.

## Portfolio integration

GitHub Pages serves the existing ARIA interface and static files; it cannot run Python/MPS inference. After reviewing a successful render, copy only the **final ARIA MP4**, not the `_concat.mp4` comparison video containing the driver, into `fpa-copilot/` and add a normal HTML `<video controls playsinline>` player. Do not publish a private driver or claim that prerecorded animation responds live. The existing approved portrait/interface is retained by this change.

## Troubleshooting without changing macOS security

- **Operation not permitted / restricted mode:** stop and copy the exact error and command. If macOS asks Terminal for Downloads access, grant access only to the required folder in Privacy & Security, or move your working folder to a location you permit Terminal to use. Organization-managed restrictions require your administrator. Do not disable Gatekeeper or SIP; do not remove quarantine recursively.
- **Conda not found:** reopen Terminal after arm64 Miniforge shell initialization. This installer uses `conda run`; no shell-hook evaluation is required.
- **Model download fails:** check the named hosting service/network, then rerun installation; downloads can resume. No token is normally required for these public model files.
- **Different portrait already exists:** the script stops instead of overwriting it. Preserve the existing image elsewhere, compare it with the approved PNG, and only then place the exact approved file at the reported path.
- **MPS/model/import error:** send the full traceback, `sw_vers`, `uname -m`, and the command used. Do not install CUDA packages or describe the setup as complete.
- **No face or poor mouth/teeth:** retain the original, start with a better-lit frontal driving video and small motion. Face crop settings may need local adjustment after reviewing the error/output.

The earlier ZIP had a relative-path copy bug after changing directories and hid copy failures. These scripts resolve their own folder before changing directories, refuse unknown portraits, pin upstream/model revisions, and never print installation success after a failed check. The former `huggingface_hub[cli]`/CLI selection is replaced with its Python download API; the retired silicon-specific ONNX package is replaced with a standard arm64-compatible wheel. CLI dependencies omit the unused Gradio web server and pin albucore to retain the API required by upstream albumentations.

## Sources and local checks

- [Official LivePortrait repository and Apple Silicon instructions](https://github.com/KlingAIResearch/LivePortrait)
- [Pinned upstream source](https://github.com/KlingAIResearch/LivePortrait/tree/9b294b3d0536135442ea73cb01e6cb3ca7029dd3)
- [Pinned human weights](https://huggingface.co/KlingTeam/LivePortrait/tree/82a4fa6735ca58432b6ce39301b4b9ee066dea47)
- [Hugging Face download API](https://huggingface.co/docs/huggingface_hub/guides/download)

LivePortrait and model dependencies retain their own licenses and usage terms. Review them before commercial use. This folder contains integration code, not a claim of authorship of the neural model.

Portable regression checks (no ML model download):
```sh
cd fpa-copilot/liveportrait
python3 -m unittest -v test_runtime
```
