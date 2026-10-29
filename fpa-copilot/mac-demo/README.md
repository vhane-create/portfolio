# ARIA Mac demo and employer demonstration

This local launcher serves the current approved ARIA interface and routes broad
questions to LM Studio on the same Mac. It needs no OpenAI API key or paid cloud
GPU. The existing browser Heart generator continues to use `af_heart`; approved
assets, finance calculations, microphone input and information entry are retained.

## Start on Netta’s Mac

1. Update/download the current `vhane-create/portfolio` repository. Keep this
   `mac-demo` folder inside its `fpa-copilot` folder, with the current page, scripts
   and approved assets. An old project ZIP will not contain this launcher.
2. In LM Studio, load a chat/instruct model compatible with the Mac’s memory.
   Open its Developer tab and start the local server on port `1234`. Keep it
   bound to localhost. The model may require a one-time download. Model quality
   determines answer quality; this launcher does not turn a small model into ChatGPT.
3. In Terminal, run the script from the downloaded project. For the previously
   used folder layout, the command is:

   ```bash
   python3 "$HOME/ARIA-Setup/fpa-copilot/mac-demo/server.py"
   ```

   Adjust the path if the new download is elsewhere. `Start_ARIA_Mac.command` is
   an alternative launcher once executable. This service uses Python’s standard
   library; it does not install Python, LM Studio or model weights.
4. The browser opens `http://127.0.0.1:8766`. Keep Terminal and LM Studio running.
   Open Voice & controls to check local-model and facial-renderer status.
   Connect the previously configured ARIA USB. The launcher uses the existing
   `~/ARIA-LivePortrait/env-heart/bin/python` when available so the local Kokoro
   dependencies are available. Type `Hello` for a short first render, then test
   a new question. Click Talk to ARIA and allow microphone access for voice input.

If multiple models are available, select one explicitly:

```bash
python3 mac-demo/server.py --model YOUR_LOADED_MODEL_ID
```

Use `--lm-port` if LM Studio uses a different local port. If LM Studio already
requires authentication, supply its existing token through `ARIA_LM_TOKEN` in the
local environment. Never place credentials in a public page or repository.

## What employers can access

- A scheduled **live Mac demonstration** can be shown through screen sharing while
  Netta runs the local service. Confirm actual microphone, answer and playback
  behavior on the Mac before presenting it.
- The public GitHub Pages portfolio remains accessible independently. This local
  service does **not** automatically make the Mac reachable from that public page.
- Unattended employer conversations need a reachable reasoning/animation backend
  or independently validated on-device inference. Neither is established by this
  launcher. No public tunnel, router forwarding or paid service is enabled.

## Animation status

The Mac page now connects each new reply to the existing local Kokoro `af_heart`
and MuseTalk renderer through `/api/reply`, `/api/job/…` and `/api/media/…`. It plays
the newly rendered video for that answer, then reopens the microphone in voice
conversation mode. Stop/new questions cancel playback and polling, and old results
cannot replace the newer answer. A render already running may finish in the
background; new renders are rejected as busy until it finishes.

Mouth movement is generated for the new Heart audio. Eye and head/neck movement
comes from the exact approved `aria-approved--d0.mp4` motion source, whose hash is
checked. This is not a new model for spontaneous eye contact or emotional reactions.
The facial-source framing is preserved; head-to-toe movement is not implemented.
It renders before playback and may take minutes. Real-time response speed has not
been established. Missing local models/USB are reported without substituting a
still image, unrelated reply video or alternate voice as a successful render.

This integration applies to the local Mac page, not public GitHub Pages. It does
not implement live full-body animation or walking.

The CUDA body-animation experiment is a separate development candidate, not part
of this Mac launcher. The researched MLX LongCat port reports 32 GB+ recommendations
for its smaller variant and about 102 seconds for 29 frames on the author’s tested
128 GB M5 Max; it is not yet a demonstrated real-time option for this MacBook Air.
No large animation-model download is triggered here.

## Privacy and limits

Reasoning requests go only to `127.0.0.1` through the local proxy. The server binds
to loopback, rejects other origins, keeps history in each browser request, serves
only supported web/media files, and does not store question text. It limits added
information to 8,000 characters and total model context to 16,000 characters.
Browser microphone recognition may use an external speech service; Heart setup
downloads model files. This is not a fully offline voice system.

Financial calculations already handled by `conversation.js` stay deterministic.
Local-model explanations and other arithmetic still need review. There is no live
web search in the LM Studio route, and ARIA must not claim current facts or sources
she did not retrieve.

## Verification

Five local HTTP tests passed against simulated LM Studio and animation services:
local page routing without cloud fallback, history/reference propagation and
separate sessions, blocked cross-origin/private-file access, and truthful missing
model errors, plus animated reply/job/media pairing. Eight Heart-service tests
passed with synthetic speech, including lazy initialization with fixed `af_heart`
and rejection of a changed motion source. JavaScript checks cover stale-video
rejection, matching playback, replay microphone suppression and reopening the
microphone after animated playback. Python and JavaScript syntax checks passed.

Not verified here: execution on Netta’s Mac, a real model’s answer quality/latency,
real microphone transcription, or a real new MuseTalk render in this integration.
Do not describe the test fixtures as successful real-model conversation or visual
proof of natural blinking, lip sync or head motion.

Official LM Studio references:
- https://lmstudio.ai/docs/developer/core/server
- https://lmstudio.ai/docs/developer/openai-compat/chat-completions

Mac animation candidate reviewed:
- https://github.com/xocialize/longcat-avatar-mlx
