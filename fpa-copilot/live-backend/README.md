# ARIA public reasoning backend

This service supplies text answers through the OpenAI Responses API. It does not generate Heart audio, facial animation, or full-body movement. Those are separate integrations.

The public `/ask` endpoint does not require a visitor access code. The OpenAI key stays in the server environment. Browser pages must never contain an API key.

Configuration:

- `OPENAI_API_KEY`: required, stored as a Render secret environment variable.
- `OPENAI_MODEL`: defaults to `gpt-4.1-mini`.
- `ALLOWED_ORIGIN`: defaults to `https://vhane-create.github.io`.
- `ENABLE_WEB_SEARCH`: optional; enables the existing company-mode search path.

Run locally with the existing requirements and `uvicorn app:app --host 127.0.0.1 --port 8080`. Deployment configuration is in `render.yaml` and `Dockerfile`.

## Availability and provider errors

`GET /health` reports whether a key is configured. It does not prove that the key has available allowance or that an actual answer succeeds.

- `503` with `X-ARIA-Error: ai_quota_exhausted`: the provider reported `insufficient_quota`; the owner needs to review API billing or allowance.
- `429` with `X-ARIA-Error: ai_rate_limited` and `Retry-After: 60`: the provider reported another rate-limit error; wait before retrying.
- Provider messages, keys, account details, and exception strings are not exposed in the response.

Existing application limits remain five questions per minute per client and sixty requests per hour across this single instance. These in-memory limits are for the portfolio demo and reset when the process restarts.

## Conversation and the five-minute conclusion

Each request contains bounded client-held history of at most twenty user/assistant messages. The service does not use shared conversation IDs, and model requests use `store=False`. Reference information is treated as untrusted data.

The prepared conclusion controller in `../employer-tour/qa-session.mjs` has a maximum 300-second session and cancels microphone capture, requests, speech and gestures at expiration. It is not connected to this service or to a live avatar renderer yet. A future streaming provider must also enforce a 300-second maximum session duration.

## Validation

Run `PYTHONPATH=fpa-copilot/live-backend python -m unittest discover -s fpa-copilot/live-backend/tests -v` from repository root after installing `requirements.txt` and `requirements-test.txt`.

Provider tests use a mocked model. They verify session isolation, input validation, public access, origin rejection, and distinct quota/rate-limit messages. Actual model responses, microphone input, Heart speech and lip synchronization require separate end-to-end verification.
