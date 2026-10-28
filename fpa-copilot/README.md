# FP&A Copilot Lab

[Live interactive prototype](https://vhane-create.github.io/portfolio/fpa-copilot/) | [Portfolio homepage](../)

This **deterministic, AI-ready** financial analysis prototype demonstrates calculation-grounded CFO commentary using a synthetic departmental expense dataset. It does **not** call an LLM or claim to evaluate model performance.

## Run verification
`node fpa-copilot/test.js`

The code validates budget and actual amounts, computes unfavorable expense variance as actual minus budget, flags departments above an adjustable percentage threshold, handles zero budgets, and produces a concise executive briefing with an explicit limitation: a variance alone cannot establish causation.

## Enterprise AI roadmap
A future LLM layer could generate alternative commentary from verified numerical outputs; a reviewer would compare those responses to finance-specific goldens and rubrics in `ai-evaluation/`. No such LLM integration or independent golden certification is claimed here.

All amounts are simulated. No proprietary employer or client data is included.
