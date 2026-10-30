# Cached facial renderer — development only

The optional `ARIA_CACHED_RENDERER=1` backend path keeps one private Python worker alive between replies. It retains UNet, VAE, Whisper, face parser, source latents, masks and frames. Heart remains `af_heart` in the existing speech pipeline. There is no HTTP listener, alternate voice provider, cloud fallback, model download, or new paid service in this worker.

Each job uses its own validated 32-character ID and matching WAV/output filename. The approved source hash is checked for every job. Existing output is preserved, escaped audio paths are rejected, and failures/timeouts terminate the worker so a later request starts fresh. Output still receives the existing ffprobe stream checks and complete ffmpeg decode. The default per-reply renderer remains selected unless the development option is explicitly enabled.

Verified October 30, 2026:

- Sixteen backend/worker tests passed, including two-job pairing, one initialization, a real persistent subprocess, timeout termination, restart, source preservation, output preservation, path checks, and integration with media validation. These tests use simulated neural output.
- A separate actual CPU neural test used full-size MuseTalk/VAE/Whisper/face-parser weights. It rendered two different 0.24-second existing Heart audio segments with the same model objects and prepared avatar; both videos decoded fully and had different hashes. Setup took 7.70 seconds, followed by 28.53 and 25.68 seconds per six-frame render. See `cached-model-validation.json`.
- That short test used one PNG extracted from the approved source to keep the test bounded. It is not a benchmark for the complete moving avatar, a new conversation, or new speech synthesis. The earlier complete three-second moving-source test is under ../docs/validation/2026-10-30/.

Caching avoids reloading/repreparing resources on every normal reply; it does not remove neural inference time. These CPU results remain far too slow for natural conversation and establish no Mac speed claim. Apple Silicon performance, simultaneous LM Studio memory use, microphone turn-taking, lower-face quality, and the complete conversation flow remain unverified. Persistent models retain memory until the local backend exits. The Mac installer stays pinned to its prior held development release, and no existing Mac installation or public page was changed. Do not distribute this option as a finished product.

Implementation: `render_engine.py` contains the dedicated neural core adapted from the bundled MuseTalk-Mac server; `render_worker.py` handles private requests; `cached_renderer.py` owns the subprocess lifecycle. Optional voice-provider/server initialization from the upstream web server is never imported.
