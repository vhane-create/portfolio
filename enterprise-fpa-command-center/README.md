# Enterprise FP&A Command Center
Financial Planning, Performance Analysis & Executive Decision Support

Primary hiring-manager entry point: `enterprise-fpa-command-center/`. The `enterprise-fpa/` model remains supporting work. The ARIA employer tour links to this flagship and the featured **Financial Modeling with NPV and IRR** Excel project.

## Reviewer walkthrough
1. Load the January-hiring business case: demand -12%, salaries +8%, 20 hires, $3m additional investment funded in April.
2. Load the connected expense sample or run `python finance-automation/report.py` and import its generated `output/forecast_bridge.json`.
3. Inspect the executive bridge, monthly seasonality, quarter totals and minimum month-end cash.
4. Compare October hiring. Review payroll savings alongside the capacity/service tradeoff.
5. Read the five-year investment valuation and management recommendation. Export the executive CSV or print the report.

All data is synthetic. This case is a demonstration of analysis, not a claimed employer result.

## Model and assumptions
- Annual revenue = plan × demand multiplier × price multiplier; monthly shares Jan–Dec: 6,6,7,7,8,8,8,8,9,10,11,12 percent.
- Starting FTE plus new hires from the selected month; loaded salary = salary × (1 + benefits).
- Variable costs flex with revenue. Fixed costs, recurring capex and debt service spread evenly.
- Operating WC is a month-end balance equal to monthly revenue × WC ratio, with an explicit opening balance. Cash absorbs the change, not the entire balance every month.
- Monthly cash tax = max(EBITDA,0) × rate; simplified proxy without depreciation or loss carryforwards. Net cash flow is after debt service.
- Additional investment plus its initial project WC is funded in the chosen month. Valuation imports the existing NPV/IRR project's five-year model, scales revenue/costs/maintenance/salvage to investment size, adjusts project revenue for demand and price, and retains a 12% hurdle. Project returns begin after this operating forecast year; no return is double counted.
- Imported expenses represent a subset of already-planned costs. Only actual-minus-budget variance is applied, once, at its quarter close. Imports must contain one reporting year, unique period/department/account keys and reconciled finite nonnegative values. This is a file handoff, not a live ERP connection. No forward extrapolation of imported variance is assumed.

## Reproduce and verify
```
python finance-automation/report.py
node enterprise-fpa-command-center/model.test.mjs
node tests/flagship-models.test.cjs
python -m unittest discover -s finance-automation -p 'test_*.py'
```
Baseline: $120m revenue, $23.648m EBITDA, $28.9184m ending cash. January-hiring case before imported costs: $9.95328m EBITDA; investment NPV approximately -$239,260 and IRR 9.30%, below the 12% hurdle. These are synthetic outputs, not audited financial statements or a full three-statement forecast.
