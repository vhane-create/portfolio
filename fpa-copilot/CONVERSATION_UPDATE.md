# ARIA conversation update

This change adds session-local dialogue to `aria-final.html` and the local Heart preview. It preserves the existing layout, portrait references, Heart settings, prerecorded media, original calculator, and unrelated portfolio files.

## Available without an AI service

- Greetings and a truthful capability overview.
- USD actual/budget figures in either order, with revenue/expense interpretation.
- Revenue percentage scenarios using the original actual and unchanged budget.
- Follow-up investigation that separates known differences from possible causes.
- Cash flow versus profit and a simpler follow-up explanation.
- Clear conversation resets figures, history, and access code and suppresses pending responses. Each page instance has separate memory; no chat is written to browser storage or a shared backend session.

This is a limited deterministic conversation layer, not unrestricted AI reasoning. Missing figures trigger clarification. Supported arithmetic runs in integer cents and checks safe numeric bounds. Scenarios are hypothetical and do not overwrite original actuals.

## Optional reasoning connection

The existing `live-backend/app.py` now accepts up to 20 user/assistant history messages. It forwards that history with the current question to the Responses API using `store=False`. It does not retain shared chat history. Official reference: https://developers.openai.com/api/docs/guides/conversation-state

Deploy and configure the existing backend before setting `meta[name="aria-reasoning-url"]` in either page to its HTTPS base URL. Its default is empty, so no model requests occur by default. Each page prompts for a restricted demo access code when first needed; Clear removes it from memory. Never enter an OpenAI API key into the page. Keep `OPENAI_API_KEY` and `DEMO_ACCESS_TOKEN` in backend environment variables, and set `ALLOWED_ORIGIN` for the page's origin. The existing shared demo access code is for controlled demonstrations, not multi-user production authentication.

In finance mode the model may now explain supplied figures and concepts, rather than always being forced into the synthetic department dataset. The dataset remains available when explicitly requested. The deterministic browser calculator handles the supported arithmetic cases before any model request.

## Speech and animation

Replies still flow through the existing `say` function. On the portfolio page only the exact existing sample answer is eligible for its recorded variance clip. New text never automatically plays that unrelated clip. On the local Heart page, the existing local server replaces `say` with its Heart/MuseTalk job flow. That service, Mac environments, model files, and USB remain necessary for new spoken animated responses. No substitute browser voice is introduced.

## Verification

Run from repository root:

```sh
node --test fpa-copilot/conversation.test.js fpa-copilot/page-conversation.test.js
node fpa-copilot/test.js
python -m pip install -r fpa-copilot/live-backend/requirements.txt -r fpa-copilot/live-backend/requirements-test.txt
PYTHONPATH=fpa-copilot/live-backend python -m unittest discover -s fpa-copilot/live-backend/tests -v
```

October 28, 2026 results: 12 Node tests, 5 Python tests, and the existing FP&A regression script passed. Page tests execute actual page scripts with a minimal DOM; provider tests mock the model. They cover follow-ups, topic changes, clearing an in-flight request, history transmission, session isolation, validation, missing credentials, and provider failure.

No real model calls, new Heart synthesis, GPU inference, audible playback, lip synchronization, or live deployment are claimed by these checks. Render connection was available during inspection, but its service listing returned no services. No hosting resources or paid services were created.
