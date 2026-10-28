# ARIA LivePortrait verification — 2026-10-28

## Verified in the development workspace

Environment: Linux x86_64, isolated CPython 3.10.22. This is not the user's Mac.

- Inspected the prior `ARIA_LivePortrait_Mac_Safe_Launch.zip` and repository scripts.
- Recovered the approved source PNG and copied it without modification. Its SHA-256 is `9889d86d17f07437243204107a91ed7ab4a49a5a9d1841ec56c59d117247d958`.
- Bash and zsh syntax checks passed for all four shell files. The installer correctly refused to install on Linux.
- Seven portable regression tests passed under both Python 3.10 and 3.12. They cover source-image integrity, refusing to overwrite a different portrait, missing/LFS model detection, invalid media, missing speech audio, paths with spaces, failed-render reporting, and a real FFmpeg/ffprobe media check. Mocked orchestration tests are not neural-render tests.
- Resolved the dependency set for CPython 3.10 / Apple Silicon macOS using uv. Downloaded actual macOS arm64 wheels for torch 2.3.0, torchvision 0.18.0, torchaudio 2.3.0 and the macOS universal2 wheel for onnxruntime 1.20.1.
- Installed the inference requirements into a separate Linux Python 3.10 environment, using the CPU PyTorch index for that Linux test only. Dependency consistency check passed for 68 installed packages.
- Imported albumentations, ONNX Runtime and the upstream LivePortrait pipeline successfully. Parsed the launcher's flags with the pinned upstream tyro configuration.
- Downloaded all eight human model files from Hugging Face revision `82a4fa6735ca58432b6ce39301b4b9ee066dea47` and loaded all neural/face models.
- Ran the pinned upstream inference pipeline with ARIA's exact portrait and the first three frames of upstream `d0.mp4`, using full-precision CPU inference, automatic driver cropping, full facial region, stitching and pasteback. The three-frame render completed successfully (about 25 seconds for animation here).
- FFprobe confirmed an 852×1280 MP4, 3 frames, 0.12 seconds. FFmpeg decoded it without errors. Inspected the first output frame: ARIA's suit, hair, background and robotic hands remain visible; the model produced an animated-face result rather than a substitute avatar.

The tiny render is a technical smoke test, uses an upstream example driver, and has no speech audio. It is not a finished ARIA introduction or evidence of realistic teeth, natural blinking, or speech synchronization. No private driver or test output was published to the portfolio.

## Still required on the MacBook Air M4

1. Run `zsh install_mac.sh` from the updated integration folder. It must complete its native arm64/MPS, face detection and single-frame neural checks.
2. Run `zsh verify_mac.sh` if any environment changes or earlier steps failed. A failed doctor removes its old success report.
3. Supply a permitted 5–10 second frontal driving video containing the intended speech, natural blinks, small head movements and mouth openings/teeth.
4. Run `zsh animate_aria.sh /absolute/path/to/driving.mp4`. Require a new final MP4 with audio, successful full decode and `render-check.json`.
5. Review identity, suit/hair/robotic details, teeth, lip timing, blinking, head motion and face/neck seams in QuickTime. A JSON success flag cannot replace this review.

No direct access to the local Mac is available in this session. No Mac installation, MPS render, realistic speech animation, or final video publication is claimed complete. No macOS security settings were changed.

