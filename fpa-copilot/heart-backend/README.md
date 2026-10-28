# ARIA local Heart replies

This service connects the existing finance page to Kokoro's `af_heart` voice and the already configured MuseTalk Mac renderer. It binds only to `127.0.0.1:8765`. It does not replace ARIA's portrait, existing pages, or portfolio index. The new page is served in memory at that address.

## Run on the configured Mac

Prerequisites: `~/ARIA-Setup/fpa-copilot/aria-heart-preview.html`, the approved portrait at `liveportrait/aria-approved.png`, the rendered introduction at `assets/ARIA_Heart_Introduction.mp4`, the isolated `~/ARIA-LivePortrait/env-heart` environment, and the previously tested MuseTalk setup. Keep the USB mounted at `/Volumes/NO NAME` for lip-sync mode.

```bash
"$HOME/ARIA-LivePortrait/env-heart/bin/python" "$HOME/ARIA-Setup/fpa-copilot/heart-backend/heart_server.py"
```

The service opens the local page. Leave Terminal running. Select a finance topic or ask a supported question. The default mode generates Heart audio and then renders a video matching that answer before playback. Each video render reloads the models; this can take several minutes and is not real-time conversation. Audio-only mode generates Heart speech without matching mouth animation. A Play latest reply button supports browsers that block delayed autoplay.

One reply can generate at a time. Stop cancels playback and polling; an already running synthesis/render can finish in the background. Another request is rejected as busy until generation completes. Results and diagnostic logs remain under `~/ARIA-LivePortrait/heart-replies`; rendered videos go to `/Volumes/NO NAME/ARIA-Live-Replies`. No automatic deletion occurs. The service checks free space, serializes work, uses CPU for Kokoro, and applies the previously successful GPU limits and batch size one for MuseTalk. These checks do not guarantee system stability.

## Capabilities and limits

- Existing actual-versus-budget calculation and finance explanations remain available.
- Heart is selected for new speech requests; browser system voices are not substituted.
- Lip-sync mode generates a new video for the requested answer using the approved source animation.
- Audio-only mode has no synchronized animation.
- It adds no new AI reasoning engine, spreadsheet import, financial forecast builder, market data feed, or unrestricted question answering. Existing encyclopedia lookups depend on network access.
- No paid API key is needed for local speech/rendering. Initial Kokoro/model downloads require internet access.
- GitHub Pages can host static assets, but cannot run this Python/GPU service. Public dynamic voice and animation need a separately hosted backend; this loopback service is not a public deployment.
- This is not the final deployment package. The final rendered assets on the user's Mac/USB must be collected before packaging.

## Validation

Six service tests exercise HTTP reply submission and WAV delivery using a synthetic test pipeline, input validation, origin/private-file rejection, page preservation, serialized generation, and renderer error propagation. JavaScript syntax is checked separately. These tests do not establish actual Kokoro or MPS rendering performance. The user's Mac has independently generated a real Heart finance test WAV and a lip-synced introduction; a full new-answer browser render must still be confirmed there.

Reuse the existing MuseTalk and LivePortrait licenses and model download terms. This service contains no model weights or replacement avatar.
