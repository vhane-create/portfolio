# Enterprise Finance Decision Lab

[Live interactive application](https://vhane-create.github.io/portfolio/decision-lab/) · [Source code](index.html) · [Portfolio homepage](https://vhane-create.github.io/portfolio/)

## Business question
Should a hypothetical enterprise approve a capital expansion? This **simulated investment committee case study** lets a reviewer change financial assumptions and evaluate a five-year unlevered cash flow investment decision.

## What to demonstrate
1. Select Base, Upside or Downside.
2. Adjust initial capex, Year 1 incremental revenue, growth, contribution margin, fixed costs, WACC, taxes and working capital.
3. Inspect NPV, IRR, discounted payback and the deterministic downside case.
4. Read the annual operating cash flow bridge and sensitivity table.
5. Export the computed case as CSV and inspect the HTML/JavaScript source.

## Formulas and assumptions
- Revenue_y = Year1Sales × (1 + growth)^(y-1)
- EBITDA_y = Revenue_y × contribution margin − annual fixed costs
- Depreciation_y = initial capex / 5 (straight line, no salvage value)
- Cash taxes_y = max(0, EBITDA_y − depreciation_y) × tax rate
- Working capital_y = revenue_y × working capital rate
- Change in WC_y = WC_y − WC_(y-1)
- FCF_y = EBITDA_y − cash taxes_y − change in WC_y + WC release in year 5
- FCF_0 = − initial capex
- NPV = sum(FCF_y / (1+WACC)^y), y=0..5
- IRR solves NPV=0 numerically via bisection, where a root is bracketed.
- Discounted payback interpolates within the year in which discounted cumulative cash flow crosses zero.
- Sensitivities change sales, margin, fixed costs and WACC individually.

## Scope and limitations
This is an **illustrative, deterministic project-level model**, not a complete three-statement forecast, valuation opinion, probability distribution, Monte Carlo model, or real corporate case. It excludes financing, debt tax shields, salvage value, tax-loss carryforwards, and detailed capex maintenance. The cash tax calculation is simplified. Stress-case NPV is not a statistical risk metric. The in-app audit checks the annual FCF bridge, not every possible input combination.

## Technology
Self-contained HTML, CSS, and JavaScript; no external dependencies. Browser interactivity is coded in JavaScript. The portfolio also contains separate Python and SQL examples. Codex-assisted work can be described as part of a broader development workflow, but this source file is not evidence that any particular coding agent ran.

All inputs and company details are **simulated** and contain no confidential employer data.
