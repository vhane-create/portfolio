# Live FP&A Copilot: OpenAI integration scaffold

This project contains the OpenAI Responses API evaluation runner (`evaluate.py`) and a FastAPI service scaffold. The **public /ask endpoint is intentionally disabled** until a trusted authentication gateway, rate limits, and spending controls are in place. Do not describe this as a deployed live model.

## Local evaluation (real, billable model calls)
```bash
cd fpa-copilot/live-backend
pip install -r requirements.txt
export OPENAI_API_KEY=YOUR_PRIVATE_SECRET
python evaluate.py
```
The runner sends three actual finance prompts to the OpenAI Responses API and prints responses for **human review**. No fake model scores are generated. `python -m unittest discover -s tests` verifies arithmetic. Never commit your API key or real employer financial data.

## Deployment
A Render Docker Blueprint is included as `render.yaml`; deployment is **not complete**. Configure secret management, gateway authentication, rate limiting, cost limits, HTTPS and audit logging before enabling the public /ask endpoint or connecting the GitHub Pages interface. CORS is not authentication. All financial data here are synthetic.
