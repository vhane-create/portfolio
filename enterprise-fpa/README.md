# Enterprise FP&A Command Center

[Launch the interactive app](https://vhane-create.github.io/portfolio/enterprise-fpa/) · [View source](index.html) · [Portfolio homepage](https://vhane-create.github.io/portfolio/)

## Executive summary
A standalone interactive financial planning and analysis simulation for an illustrative subscription-services business. It is designed to demonstrate the intersection of **Senior FP&A**, financial modeling, frontend coding, and analytical quality controls.

## Live capabilities
- 12-quarter driver-based financial outlook.
- Base, upside and downside scenario presets.
- Adjustable quarterly customer growth, annual price growth, service cost ratio, hiring pace, and nonpayroll operating expense growth.
- Year 1–3 management summary: revenue, cost of service, payroll, other operating expenses, EBITDA, EBITDA margin, free cash flow and ending cash.
- Interactive revenue and EBITDA chart; Year 3 operating bridge; quarterly detail table.
- Download the calculated quarterly forecast as CSV.
- In-browser reconciliation of EBITDA to its components and finite-number checks.

## Simplified assumptions
- Starting customers: 4,200; quarterly customer growth adjustable.
- Starting annual contract value: $18,000; annual price growth adjustable.
- Revenue = average quarterly customers × annual contract value / 4.
- Starting headcount: 82; hiring pace adjustable; annual loaded salary starts at $148,000 with 3.5% annual growth.
- Starting quarterly other operating expenses: $2.15 million, grown at the adjustable annual rate.
- Cost of service = modeled revenue × adjustable service cost percentage.
- EBITDA = revenue − service cost − payroll − other OpEx.
- Illustrative cash taxes = 23% of positive EBITDA less a $420,000 quarterly proxy adjustment. **Not a formal tax model.**
- Working-capital investment = 7% of positive incremental revenue relative to the prior quarter.
- Quarterly capex starts at $560,000 and increases 2.5% annually.
- Free cash flow **proxy** = EBITDA − illustrative cash taxes − working-capital investment − capex.
- Starting cash = $9 million; cash rolls forward with the FCF proxy. No debt, financing, deferred revenue, full working-capital schedule, or GAAP three-statement linkage is modeled in this interactive app.

## What this demonstrates
Financial scenario design, financial drivers, expense planning, workforce modeling, management reporting, cash-flow reasoning, interactive HTML/CSS/JavaScript, SVG chart generation, CSV exports, and model reconciliation.

## Provenance and limitations
All inputs and results are simulated. The app is a portfolio demonstration, not an employer deliverable or production finance system. The underlying HTML/CSS/JavaScript is reviewable; it should not be described as Python, SQL or Power BI source code. Those skills are demonstrated separately by the [Python project](../python/), [SQL project](../sql/) and [Excel/SQL case study](../finance-projects.html). Codex-assisted development is a portfolio workflow interest; do not imply a specific tool execution unless documented. No browser-based end-to-end test suite has yet been committed.
