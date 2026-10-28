# ARIA public conversation service — pending live deployment

This is a separate version of ARIA. The approved portrait, original demo, Heart
introduction, finance sample videos, and portfolio remain unchanged.

## What this adds

- An actual model request for each new question; the last six completed exchanges
  are supplied as context for follow-ups. No canned variance answer substitutes
  for unrelated questions.
- New Kokoro `af_heart` speech for the answer, generated on the server. No browser
  system voice is substituted. The approved portrait displays during new speech.
- Exact Decimal arithmetic for explicit actual/budget variance questions.
- Clear conversation, replay, mute and stop; model and speech failure states.
- A persistent CPU voice pipeline, one active generation, and an instance-wide
  hourly request limit. No chat database or audio files are written by the app.

**New spoken answers are audio-only.** Matching lip movements require an additional
hosted animation renderer; they are not implemented by this service. Existing
introduction and variance MP4s remain available with their original lip sync.
This is turn-based conversation, not simultaneous streaming speech.

## Deploy from vhane-create/portfolio

Create a Docker web service from the branch containing this change:

- Dockerfile: `fpa-copilot/conversation-backend/Dockerfile`
- Build context: repository root (`.`)
- Health path: `/health`
- Start command: use the Dockerfile's default command
- Public landing page: `/` (serves `aria-conversation.html`)
- `OPENAI_API_KEY`: required secret, entered through the host's secure settings
- `OPENAI_MODEL`: optional, default `gpt-4.1-mini`
- `ARIA_PUBLIC_ORIGIN`: exact final HTTPS service origin, with no path
- `ARIA_REQUESTS_PER_HOUR`: optional, default `60`, per running instance
- `PORT`: supplied by the host

The Docker build downloads Kokoro weights and the fixed Heart voice from their
upstream repository. It needs network access and enough build memory. Select host
resources only after reviewing current charges. CPU memory, cold-start latency,
Heart synthesis latency and concurrency must be measured on the actual host.
The container build has not been exercised in this environment.

Keep one instance for the current instance-local queue and usage limit. The cap is
not a billing guarantee or access control; configure an upstream provider budget
and managed protection before broad promotion. No API key belongs in HTML,
JavaScript, the Git repository, a URL or a chat message.

Serving the page and API from the same Render origin avoids cross-origin secrets
or a public demo access token. After live tests pass, link that service from the
existing portfolio. GitHub Pages alone still cannot run this service. Do not
replace the working `aria-final.html` until the new service is verified.

## Validation completed here

Run `python3 -m unittest discover -s fpa-copilot/conversation-backend -p 'test_*.py'`
and `node --check fpa-copilot/conversation.js` from repository root.

Nine tests pass using controlled model/speech substitutes: follow-up history,
new answer/audio transport, role/input rejection, private-source rejection,
origin and queue/usage limits, speech failure, provider failure, missing setup,
provider input/storage settings, and deterministic variance arithmetic.
These tests verify integration behavior, not real model or Heart inference.

## Acceptance before calling this live

1. Docker build succeeds and `/health` reports ready with the configured model key.
2. Ask "What is a forecast?" and then "How is that different from a budget?".
   Verify distinct coherent responses and new Heart audio for both.
3. Ask an unrelated ordinary question; confirm it does not replay the variance video.
4. Confirm intro and sample MP4 playback, mute, stop, replay and Clear conversation.
5. Confirm mobile playback/autoplay behavior and microphone support in a real browser.
6. Inspect latency and resource usage, set a suitable spending limit, then update the
   portfolio link. Do not claim new lip sync until an animation renderer is connected.

Reference APIs: https://developers.openai.com/api/reference/resources/responses/methods/create
Voice model and license: https://huggingface.co/hexgrad/Kokoro-82M
Hosting: https://render.com/docs/docker and https://render.com/docs/web-services
