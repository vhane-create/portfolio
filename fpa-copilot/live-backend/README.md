# ARIA — live conversational finance AI backend

**Status: source code committed; deployment and actual model inference are not yet verified.**

ARIA is a humanlike animated avatar at [ARIA display](https://vhane-create.github.io/portfolio/fpa-copilot/aria.html) with browser speech synthesis, optional speech recognition, and a real OpenAI Responses API backend. This is a **model-powered application**, not a foundation model trained from scratch.

## Run locally
```bash
cd fpa-copilot/live-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="set-this-in-a-private-environment-only"
export DEMO_ACCESS_TOKEN="generate-a-random-secret-at-least-24-characters"
export OPENAI_MODEL="gpt-4.1-mini"
python -m unittest discover -s tests
uvicorn app:app --host 127.0.0.1 --port 8080
```
For a hosted demo, deploy the Docker service using the included Render configuration, set `OPENAI_API_KEY` and `DEMO_ACCESS_TOKEN` in the hosting provider's **secret environment variables**, and restrict `ALLOWED_ORIGIN` to the portfolio origin. Never put secrets in GitHub, HTML, or client JavaScript. In ARIA's UI, enter the HTTPS backend URL and demo access code privately; the page does not persist them.

## What is real?
- The avatar visibly animates and speaks using browser text-to-speech, without prerecorded dialogue.
- The microphone uses browser speech recognition when supported and authorized.
- The authenticated `POST /ask` route makes **real, billable** OpenAI Responses API calls when configured and deployed.
- The finance context is deterministic and synthetic; output is AI-generated and **not automatically verified**.
- `evaluate.py` makes additional billable API calls for human review, but does not manufacture scores.

## Security and production limitations
The service checks a constant-time bearer token, caps prompt length and model output, uses a simple five-requests-per-minute-per-IP in-memory limiter, sets a single allowed CORS origin, and uses `store=False` for model requests. **CORS is not authentication.** This is a **private demonstration architecture**, not production security. For public access use a managed API gateway, per-user authentication, distributed rate limiting, abuse monitoring, provider spend caps, observability, secret rotation, and independent security review. Browser speech recognition may use the browser vendor's service; do not enter confidential or personal information.

The backend does not yet support document uploads, persistent conversations, streaming speech, or 3D animation. It does not prove AI correctness. No external service has been deployed by these GitHub commits.

