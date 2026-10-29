# ARIA — live conversational finance AI backend

**Status: source code committed; deployment and actual model inference are not yet verified.**

ARIA's final portfolio page is `../aria-final.html`, and her local Heart page is `../aria-heart-preview.html`. This optional backend supplies text reasoning through the OpenAI Responses API. Her approved Kokoro Heart voice and MuseTalk animation remain separate services. See `../CONVERSATION_UPDATE.md` for the connection and verified checks.

## Run locally
```bash
cd fpa-copilot/live-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
export OPENAI_API_KEY="set-this-in-a-private-environment-only"
export DEMO_ACCESS_TOKEN="generate-a-random-secret-at-least-24-characters"
export OPENAI_MODEL="gpt-4.1-mini"
python -m unittest discover -s tests
uvicorn app:app --host 127.0.0.1 --port 8080
```
For a hosted demo, deploy the Docker service using the included Render configuration, set `OPENAI_API_KEY` and `DEMO_ACCESS_TOKEN` in the hosting provider's **secret environment variables**, and restrict `ALLOWED_ORIGIN` to the portfolio origin. Set the page's `aria-reasoning-url` meta tag to the HTTPS backend base URL; leave it empty to keep model requests disabled. The page prompts for a restricted demo access code when needed, retaining it in memory until Clear or reload. Never put provider API keys in GitHub, HTML, or client JavaScript.

## What is real?
- The final portfolio page uses included Heart videos for its introduction and exact recorded example. New speech requires the local Heart service; this backend does not generate speech or animation.
- The microphone uses browser speech recognition when supported and authorized.
- The authenticated `POST /ask` route makes **real, billable** OpenAI Responses API calls when configured and deployed.
- Supported browser calculations are deterministic. The model can explain user-supplied figures or the explicitly requested synthetic department example; model output is **not automatically verified**.
- Each request includes at most 20 client-held history messages for follow-ups. The service stores no shared conversational history.
- `evaluate.py` makes additional billable API calls for human review, but does not manufacture scores.

## Security and production limitations
The service checks a constant-time bearer token, caps prompt length and model output, uses a simple five-requests-per-minute-per-IP in-memory limiter, sets a single allowed CORS origin, and uses `store=False` for model requests. **CORS is not authentication.** This is a **private demonstration architecture**, not production security. For public access use a managed API gateway, per-user authentication, distributed rate limiting, abuse monitoring, provider spend caps, observability, secret rotation, and independent security review. Browser speech recognition may use the browser vendor's service; do not enter confidential or personal information.

The backend does not yet support document uploads, persistent conversations, streaming speech, or 3D animation. It does not prove AI correctness. No external service has been deployed by these GitHub commits.


