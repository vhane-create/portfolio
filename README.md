# Vannetta Haney | FP&A and Financial Analysis Portfolio

[View portfolio](https://vhane-create.github.io/portfolio/) · [Excel and SQL case study](https://vhane-create.github.io/portfolio/finance-projects.html) · [Scenario dashboard](https://vhane-create.github.io/portfolio/salon-dashboard/)

I focus on strategic finance and FP&A: budgeting, forecasting, variance analysis, scenario modeling, and checking financial information against its source. This repository brings together working financial samples and their documentation.

## Start with these projects

| Project | Business question | Tools | Review |
| --- | --- | --- | --- |
| Excel budget versus actual | Where did operating profit miss budget? | Excel formulas and native chart | [Workbook](Vannetta_Haney_Excel_Budget_Analysis.xlsx) · [Case study](https://vhane-create.github.io/portfolio/finance-projects.html) |
| SQL financial variance analysis | Do transaction totals reconcile, and which categories drive the shortfall? | SQLite, joins, CTEs, window functions | [SQL and checks](sql/) · [README](sql/README.md) · [ZIP](Vannetta_Haney_SQL_Finance_Project.zip) |
| Salon Business Dashboard | How do volume and price changes affect profit and break-even? | JavaScript, HTML, CSS, scenario controls, CSV export | [Live dashboard](https://vhane-create.github.io/portfolio/salon-dashboard/) · [Model and tests](salon-dashboard/README.md) |

All three use **simulated data**. They are personal portfolio demonstrations, not employer deliverables or actual salon financial results.

## Excel and SQL variance case study

**Purpose:** compare budget with actual results and identify priorities for a monthly finance review.

**Inputs and assumptions:** illustrative October 2026 reporting month; USD. Revenue is $100,000 budget / $95,000 actual. Expenses include payroll, supplies, and rent only. This is a simplified operating-profit analysis.

**Logic:** variance equals actual minus budget. Expense increases reduce profit; revenue increases raise profit. SQL aggregates transactions before joining to budget so the budget is not duplicated. Missing data remains distinct from an explicit zero. Zero budget produces an undefined percentage rather than a misleading percentage.

**Results:** budgeted operating profit is $35,000 and actual profit is $24,000, an **$11,000 unfavorable variance**. Revenue contributes $5,000 of the shortfall, payroll $3,000, and supplies $3,000. Rent is unchanged.

**Management interpretation:** revenue explains roughly 45.5% of the profit gap. Review revenue detail first, then payroll hours/rates and supply quantities/prices. The numbers identify contributors; they do not establish causes.

**Verification:** source-to-report reconciliation and checks for duplicate keys, missing actuals, explicit zero actuals, zero budget, and actual-only categories are documented in the [SQL README](sql/README.md). Compare the workbook totals with the SQL baseline outputs.

### Open and reproduce

Download the Excel workbook and open it in Excel; inspect inputs, formulas, and the linked chart. For SQL, use SQLite 3.25 or newer and a fresh database:

```sh
sqlite3 finance.db < sql/01_setup.sql
sqlite3 -header -column finance.db < sql/02_analysis.sql
sqlite3 -header -column finance.db < sql/03_checks.sql
```

The checks should return no rows. See [SQL documentation](sql/README.md) for setup details and limitations.

## Driver-based scenario model

The [Salon Business Dashboard](https://vhane-create.github.io/portfolio/salon-dashboard/) models two locations using appointment volume, average service price, per-visit supply cost, and fixed expenses.

- Revenue = appointments × average price.
- Operating profit = revenue − appointment supply costs − fixed expenses.
- Break-even appointments = fixed expenses ÷ contribution per appointment, rounded up when attainable.

The baseline produces **$25,700 revenue and $11,420 operating profit**. Change volume and price to test sensitivity, compare locations with fixed sample budgets, and export scenario results. The model assumes a constant service mix and excludes taxes and financing.

[Read assumptions, calculation rules, input validation, and test coverage](salon-dashboard/README.md).

```sh
node salon-dashboard/model.test.js
```

## Relevant learning

**Financial Modeling and Analysis Specialization — Corporate Finance Institute | October 2026**

Completed courses: Operational Modeling; Reading Financial Statements; Financial Analysis Fundamentals; Corporate & Business Strategy.

Additional credentials and verification links are maintained in the [portfolio credentials section](https://vhane-create.github.io/portfolio/#credentials).

## Additional creative demonstrations

[House design](demos/houses.html), [bird animation](demos/birds.html), and [airplane dashboard](demos/planes.html) are separate interactive web demonstrations. They are not financial models. Existing source and examples remain available under `demos/`.

## Project direction and implementation

I selected the portfolio content and business use cases, reviewed results, and directed revisions. Codex assisted with implementation and verification. These samples demonstrate financial reasoning, model review, and project direction; they do not claim machine-learning forecasting capability.

## Repository layout

- `index.html`: professional portfolio and credentials
- `finance-projects.html`: Excel/SQL case study and downloads
- `sql/`: setup, analysis, checks, and baseline outputs
- `salon-dashboard/`: scenario dashboard, calculation model, and tests
- `demos/`: additional creative demonstrations

The website uses GitHub Pages. Static pages can be opened in a browser; the financial dashboard's tests require Node.js.
