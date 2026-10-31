# ARIA: tested alternatives and remaining live requirements

The public portfolio tour has not been replaced or changed by this work.

## Working evidence

- MuseTalk 1.5 installed in an isolated environment and actually executed on CPU.
- A two-second internal mouth-rendering check completed with all 60 faces detected. This is a technical check, not a replacement tour scene.
- The entire 30-second source conclusion is preserved. Its original body, camera and environment are retained; only the speaking face region is repainted from the exact af_heart recording. The resulting MP4 is a review candidate, not a live question session or a claim of perfect visual synchronization.
- Qwen2.5-1.5B-Instruct actually answered creator, NPV/IRR and profit/cash-flow questions locally. Recorded timings were about 10–22 seconds per answer under concurrent rendering load. This is an evaluation, not broad financial validation.
- The 0.5B model was rejected after factual and persona failures. The 1.5B model also needed an explicit free-time identity guard. Do not silently promote either raw model to production or claim ChatGPT-level quality.
- The five-minute controller has 11 passing tests. The candidate streaming adapter has four passing browser-interface tests and four server token tests, using mocks. These tests do not establish a working external avatar stream.

## Offline rendering route

`render_heart_musetalk.py` uses the inspected Apple Silicon MuseTalk fork at commit `7fd019315127d7f31e2e7f9853547ddceabbeb6e`.
The fork omitted `musetalk/models/vae.py` and `unet.py`; they were restored from the official Tencent repository, commit `0a89dec45a0192b824e3cf4daf96c239440c5ed8`.
Weights came from the official model repositories and the upstream face-parser download link. Their hashes are recorded separately.
The source video and Heart audio must be supplied. Audio longer than the source is rejected: the renderer does not pad, freeze or loop the source video.
`--speech-ranges` keeps original frames outside spoken passages. `--small-face-fallback` detects distant faces in the walking shot before landmark processing.
Ten transient walking-shot detector gaps were repaired with face boxes interpolated from adjacent detected frames. Only crop positions were interpolated; whole video frames were not frozen or repeated.
CPU rendering is far too slow for natural live replies. The Mac M4 route has not been benchmarked here.

## Candidate for live seated Q&A

Simli's documented client accepts supplied audio as PCM16, 16 kHz, mono. This permits af_heart rather than a replacement voice.
`avatar_token.py` mints a server-side session with `maxSessionLength=300`. It requires a server-only API key and the actual approved custom ARIA face ID. It refuses to substitute a stock face.
`simli-avatar.mjs` sends Heart PCM to the avatar player and closes local media at the deadline. It is not imported by the published tour.

The inspected pricing page lists the custom-avatar Hobby plan at $10/month, with 1,000 minutes/month and one custom generation/month. The free plan lists template avatars. These are published terms, not an account entitlement or purchase.
The inspected Trinity-2 documentation describes waist-up avatars, torso and hands, and about four hours to create a custom face. On-command animation is marked coming soon. This is a candidate for seated conversation, not proof of full-body walking or a handshake.

Still needed for a public end-to-end session: an authorized custom-avatar account and approved trained result; a functioning reasoning service (the current Render request returned HTTP 429); a deployed Heart speech endpoint; microphone/transcription integration; and real gesture assets for the approach/repeat and handshake actions. No new paid plan has been activated.

Official references checked: https://github.com/TMElyralab/MuseTalk ; https://github.com/barnent1/musetalk-mac ; https://www.simli.com/pricing ; https://docs.simli.com/api-reference/trinity-2 ; https://github.com/simliai/simli-client .
