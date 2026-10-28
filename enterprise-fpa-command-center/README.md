# Enterprise FP&A Command Center — Flagship 07

An integrated **synthetic** finance management demonstration covering revenue, variable costs, fixed costs, loaded workforce expense, EBITDA, cash taxes, capital spending, debt service, working-capital investment, free cash flow, quarterly cash roll-forward, and management liquidity limits.

**Live page:** https://vhane-create.github.io/portfolio/enterprise-fpa-command-center/

## Try it
1. Change volume, pricing, cost ratio, headcount or other assumptions.
2. Inspect the scenario-versus-plan bridge and quarterly operating outlook.
3. Check whether cash stays above the management floor in each quarter.
4. Export the executive CSV, reset the baseline or print the report.

## Calculation notes
- Revenue = baseline revenue × (1 + demand %) × (1 + price %).
- Variable expense = scenario revenue × variable cost ratio.
- Payroll = average FTE × salary × (1 + benefits %) / 1,000,000.
- EBITDA = revenue − variable expense − fixed expense − payroll.
- Cash tax = max(0, EBITDA) × cash tax rate. **Simplification:** this is not a corporate income tax forecast.
- Free cash flow (illustrative) = EBITDA − cash tax − capex − debt service − revenue × working-capital investment %.
- Quarter-ending cash = opening cash + cumulative one-quarter shares of annual free cash flow.

All figures in USD millions except FTE, salary and percentages. Annual flows are allocated evenly by quarter. This is **not** a full three-statement forecast, GAAP reconciliation, employee-level payroll model, debt schedule, or real-time ERP integration. No actual client or employer information is used.

## Controls
- Required, finite and bounded input validation.
- Invalid input clears report outputs to avoid stale figures.
- Annual-to-quarterly arithmetic reconciliation.
- Quarter-level liquidity floor check.
- Nonnegative EBITDA check.
- CSV includes both scenario outputs and assumptions for reproducibility.

## Verification still needed
Run interactive cross-browser checks and independent model formula review before describing as production ready.
