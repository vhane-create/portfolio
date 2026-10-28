# ARIA — run and GitHub Pages deployment guide

ARIA preserves the exact approved Black female android portrait, long wavy black hair, black executive business suit and subtle robotic details. Her selected voice is **Kokoro Heart, `af_heart`**. The portrait, introduction and a generated finance reply are included. The user confirmed Heart's voice and matching lip movements for both speaking videos.

## Start here

| Goal | Open/run | What works |
|---|---|---|
| Preview the portfolio without installation | `aria-final.html` | Introduction and verified finance video, finance text explanations and calculations |
| Generate a new spoken, animated answer on the configured Mac | `launch_aria.command` | Local Heart synthesis and MuseTalk rendering; keep the USB and Terminal connected |
| Review the original FP&A dashboard | `index.html` | Synthetic department calculations and materiality slider |
| Check implemented vs missing features | `FEATURE_STATUS.md` | Test evidence, API/backend needs and limitations |

The old prototypes are retained as source/history. `aria-final.html` is the final static portfolio entry; it uses the exact portrait and the real included speaking videos. It does not use a substitute avatar or browser system voice. The introduction and the 120,000-versus-100,000 variance answer can play immediately from bundled media. Other text replies on that static page need the local service to become new Heart audio/video.

## Run on Netta's already configured Mac

1. Unzip into a **new directory**, rather than extracting over the existing portfolio.
2. Keep the USB mounted as `/Volumes/NO NAME`. Existing models and environments remain under `~/ARIA-LivePortrait` and the USB.
3. Open Terminal, type `zsh ` (including the space), drag `launch_aria.command` from this unzipped `fpa-copilot` folder into Terminal, and press Return. Alternatively, from inside this folder:
   ```bash
   zsh launch_aria.command
   ```
4. The local page opens at **http://127.0.0.1:8765**. Leave that Terminal window running. If another ARIA service already uses that port, stop that previous service after its current render finishes before launching this copy.
5. Click Calculate variance or ask a supported finance question. **Heart with lip sync** generates audio and then a matching video before playback. **Heart audio only** speaks sooner and has no synchronized mouth animation. If delayed autoplay is blocked, click **Play latest reply**.

Each video render reloads models and takes minutes. The tested 16.925-second finance reply rendered 423 frames. The source head/expression motion cycles to cover longer audio. This is functional asynchronous rendering, not instant streaming conversation. Stop ends playback/polling; work already rendering can finish in the background. Only one reply generates at a time. There is no paid API key for this local flow.

The launcher selects this unzipped project automatically. Advanced overrides are `ARIA_ROOT` (existing runtime directory), `ARIA_PROJECT` (project source) and `ARIA_USB` (mount used for generated video). Existing model symlinks must still point at their actual model storage. The exact original Mac-tested backend is preserved at `docs/originals/heart_server.mac-verified.py`; the packaged backend only adds project/runtime/USB path configuration and a packaged-source-animation fallback.

## Recreate on another Apple Silicon Mac

Requires native arm64 macOS, Python 3, Apple Command Line Tools and [Miniforge arm64](https://github.com/conda-forge/miniforge/releases). Keep ample free internal storage for environments and swap, plus several GB on the USB for checkpoints. Do not format a drive that contains files you need.

From this `fpa-copilot` folder:
```bash
python3 setup_runtime.py --download-models
zsh launch_aria.command
```

The installer retains existing environments and code, refusing conflicting model/source paths. It copies the bundled patched MuseTalk source only if the runtime folder does not already exist, creates separate Python 3.11 animation and Heart voice environments when absent, and downloads checkpoints to the mounted USB. Model downloads are explicitly enabled by the flag. Initial Kokoro and English language-model downloads occur on first use. Dependencies are pinned where used in the working installation; downloaded model repositories and unpinned transitive dependencies can still change.

**Fresh-machine recreation is supplied but not end-to-end verified on a second Mac.** The already configured Mac flow was user-confirmed. Review `setup_runtime.py` and dependency files before running. A failed or partial environment is retained for diagnosis, not silently deleted. The script does not reset or overwrite environments. The older independent LivePortrait installer is in `liveportrait/`; a pre-rendered approved source animation is included, so LivePortrait inference is not necessary for every new reply.

## Deploy static portfolio playback to GitHub Pages

Repository: https://github.com/vhane-create/portfolio  
Target project directory: `fpa-copilot/`

1. Back up or commit current local changes and inspect `git status`. Compare this package with the repository before copying; do not replace the repository root or existing portfolio wholesale.
2. Add the new `aria-final.html`, `assets/`, approved portrait and supporting source/docs inside the existing `fpa-copilot/`. Keep the current `index.html` and other portfolio files unless you intentionally choose to update them.
3. Link from the portfolio to `fpa-copilot/aria-final.html`. When the existing Pages deployment publishes that file, its URL is:
   https://vhane-create.github.io/portfolio/fpa-copilot/aria-final.html
4. Use the repository's existing Pages workflow/source. If no Pages deployment exists, select the intended branch and root folder in repository Settings → Pages after reviewing its current configuration. No Python install or frontend build is needed for static playback.
5. Verify the introduction and the included finance reply, the portrait, and the text calculation after publication. Public deployment of this final entry has **not** been performed by packaging.

**GitHub Pages cannot execute Python, Kokoro or GPU rendering.** Visitors can play the included videos there. Newly generated public voice/animation requires a separately hosted, authenticated generation backend, which is not deployed in this package. The local service intentionally binds only to loopback and is not designed to expose your Mac publicly.

## Optional API-based reasoning

The separate `live-backend/` folder contains a FastAPI/OpenAI demonstration. It needs `OPENAI_API_KEY`, `DEMO_ACCESS_TOKEN` (at least 24 characters), a deployed backend and configured origin. Read its own README. Do not put keys into HTML, GitHub or this ZIP. That backend is not connected to the working Heart preview and was not acceptance-tested with a real API call.

## Files and dependencies

- `assets/`: exact MP4/WAV media, including the introduction and accepted variance answer.
- `liveportrait/aria-approved.png`: unchanged approved portrait; SHA-256 `9889d86d17f07437243204107a91ed7ab4a49a5a9d1841ec56c59d117247d958`.
- `aria-heart-preview.html`: local service base, retaining the original finance interactions.
- `heart-backend/`: local voice/video service, requirements, automated tests and accepted-working status.
- `working-runtime/`: exact three source files recovered from the working Mac.
- `third_party/`: pinned LivePortrait and MuseTalk text source snapshots, configuration and license notices; patched MuseTalk files match the uploaded working code.
- `voice-config.json`: Heart voice, sample rate and successful render settings.
- `MODEL_ASSETS.md`: required external checkpoints; large model weights are not inside this ZIP.
- `VALIDATION_REPORT.json` and `SHA256SUMS.txt`: packaging verification and integrity records.
- `docs/originals/`: checked legacy readmes, exact uploaded base page and original Mac-verified server.

There are no separate blendshape/viseme/3D rig files because this implementation generates facial video with neural models. Working source animation and completed videos are included instead.

## Tests

```bash
node test.js
python3 -m unittest discover -s heart-backend -p 'test_*.py'
python3 -m unittest discover -s liveportrait -p 'test_*.py'
```

Service tests use a synthetic audio pipeline to test orchestration, not a fake claim that real ML generation occurred in the packaging workspace. See `FEATURE_STATUS.md` and `VALIDATION_REPORT.json` for exact evidence and verification limits.

## Licensing

Read `THIRD_PARTY_NOTICES.md` before redistribution or commercial use. Model code licenses do not automatically license every checkpoint. LivePortrait's upstream license identifies **InsightFace model weights as non-commercial research only** and calls for replacing those detection models for commercial use. They are not bundled here. The generated portrait/media were supplied and approved by the project owner; this archive makes no new third-party likeness or commercial-rights warranty.

