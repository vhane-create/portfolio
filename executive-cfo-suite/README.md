# Executive CFO Reporting & Decision Suite

**Live demo:** https://vhane-create.github.io/portfolio/executive-cfo-suite/

A board-style operating review built for a senior FP&A portfolio. **Every figure is synthetic.** No claim is made that the numbers came from an employer, client, or audited filing.

## Business question
How should finance explain an EBITDA shortfall and present management with transparent options?

## Baseline (USD millions)
| Metric | Budget | Actual |
|---|---:|---:|
| Revenue | 120 | 114 |
| COGS | 42 | 42 |
| Payroll | 33 | 34 |
| Other operating costs | 18 | 16 |
| EBITDA | 27 | 22 |

EBITDA variance = **−$5m**. Bridge: revenue −$6m, COGS $0m, payroll −$1m, other operating cost savings +$2m, totaling −$5m.

## Scenario logic
- Revenue = 114 × (1 + revenue adjustment).
- Payroll = 34 × (1 + payroll adjustment).
- Other operating costs = 16 × (1 + operating cost adjustment).
- COGS is constant at 42 in this deliberately simplified sensitivity.
- EBITDA = revenue − COGS − payroll − other operating costs.
- EBITDA margin = EBITDA / revenue.
- EBITDA variance = scenario EBITDA − 27.
- Bridge = (scenario revenue − 120) − (scenario COGS − 42) − (scenario payroll − 33) − (scenario other operating costs − 18).

## Manual acceptance checks
1. At reset: revenue 114, EBITDA 22, margin 19.3%, variance −5; bridge equals variance.
2. At +10% revenue and unchanged costs: revenue 125.4, EBITDA 33.4, variance +6.4.
3. At +10% payroll and unchanged other inputs: payroll 37.4, EBITDA 18.6, variance −8.4.
4. At −10% other operating costs: other costs 14.4, EBITDA 23.6, variance −3.4.
5. Reset returns all controls to zero; Print produces a printable report.

## Scope and limitations
This is an interactive **operating-statement sensitivity**, not a complete three-statement model or ERP implementation. The model deliberately keeps COGS fixed and does not calculate working capital, capex, financing, tax, or cash flow. Results must not be presented as historical employer performance. A future version can add integrated balance sheet, cash flow, monthly time series, controls, and automated tests.

## Related flagship projects
- [Enterprise FP&A Command Center](../enterprise-fpa/)
- [Investment Decision Lab](../decision-lab/)
- [FP&A Copilot](../fpa-copilot/)
- [AI Evaluation](../ai-evaluation/)
