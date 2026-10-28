# Vannetta Haney | FP&A and Financial Analysis Portfolio

[View portfolio](https://vhane-create.github.io/portfolio/) · [Excel and SQL case study](https://vhane-create.github.io/portfolio/finance-projects.html) · [Scenario dashboard](https://vhane-create.github.io/portfolio/salon-dashboard/)

I focus on strategic finance and FP&A: budgeting, forecasting, variance analysis, scenario modeling, and checking financial information against its source. This repository brings together working financial samples and their documentation.

## Featured Specializations

My completed Coursera specializations span FP&A, financial modeling, corporate risk, leadership, and business intelligence:

- **Financial Engineering and Risk Management** — Columbia University
- **Strategic Business Leadership** — University of Glasgow
- **Google Project Management** — Google
- **Python, Bash and SQL Essentials for Data Engineering** — Duke University
- **Excel Skills for Business** — Macquarie University
- **Financial Reporting** — University of Illinois Urbana-Champaign
- **Cost Accounting** — Technical University of Munich
- **Financial Planning & Analysis and Performance Management** — John Wiley & Sons
- **Financial Modeling and Analysis** — Corporate Finance Institute

**Professional Certificate:** Google Business Intelligence — Google (2026). **Treasury-related course:** Working Capital and Cash Management Essentials — EDUCBA (2026).

[Review all verified credentials](https://vhane-create.github.io/portfolio/#credentials).

## Excel for Business — Featured Capability

**Excel Skills for Business: Intermediate I — Macquarie University**, completed October 26, 2026; grade **97%**. [Verify course credential](https://www.coursera.org/account/accomplishments/verify/8H9Z7YHEIQM1).

Start with the [Excel budget-versus-actual case study](https://vhane-create.github.io/portfolio/finance-projects.html): review the working formulas, chart, and an $11,000 unfavorable operating-profit variance. The companion SQL project independently reconciles the same simulated inputs. This course credential is separate from my completed specializations; the workbook is a personal simulation.

## Technical Projects

Personal simulations with downloadable files, documented assumptions, and reviewable calculations.

### Featured projects

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

## Professional Experience

- **Uber — Strategic Finance, Revenue Planning & FP&A | 2021–2025:** forecasting, budgeting, variance analysis, financial models, and management reporting.
- **Handshake — Contract Data Evaluation & Quality Assurance | 2026–Present:** structured evaluation, source verification, and error documentation.
- **Mercor — Contract FP&A Analyst (Independent Contractor) | August–October 2026:** financial calculation and forecast review.
- **Beautiunlimited Salon and Spa LLC — Owner / Hairstylist | 2020–Present:** business operations across two locations.
- **University of Illinois Springfield — Student Research Assistant, Chemistry | June 2026–Present:** literature review, data organization, and technical documentation.
- **SIU School of Medicine — Student Hotspotting Participant | October 2025–March 2026:** interdisciplinary student case reviews and information synthesis.
- **NEMT LLC — Medical Transport | 2016–2018.**
- **Springfield Fire Department — EMT / Firefighter I | 2012–2015.**

## Education

- **DeVry University:** Bachelor’s Degree, Business & Finance, 2003–2007.
- **Lincoln Land Community College:** Associate of Biology, 2010–2012.
- **University of Illinois Springfield:** BS in Biology, in progress; Pre-Medical Studies, 2025–Present.
- **University of Spa & Cosmetology Arts:** Cosmetology Diploma, September 2023; 1,500 instructional hours.

## Certifications & Specializations

Completed learning credentials are listed separately from employment and personal projects.

### Specializations

- **Financial Engineering and Risk Management Specialization — Columbia University**, October 2026.
- **Strategic Business Leadership Specialization — University of Glasgow**, October 2026.
- **Google Project Management Specialization — Google**, October 2026.
- **Python, Bash and SQL Essentials for Data Engineering Specialization — Duke University**, October 2026.
- **Excel Skills for Business Specialization — Macquarie University**, October 2026.

- **Financial Reporting Specialization — University of Illinois Urbana-Champaign**, October 26, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/specialization/JCRHAUSJIDLP).
- **Cost Accounting Specialization — Technical University of Munich (TUM)**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/specialization/3TIK9IM7G333).
- **Financial Planning & Analysis and Performance Management — Specialization — John Wiley & Sons**, October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/specialization/GL29W3RGC8PN).
- **Financial Modeling and Analysis — Specialization — Corporate Finance Institute**, October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/specialization/6SGTM35J92TP).

### Certifications

- **Google Business Intelligence Professional Certificate — Google**, October 2026.

- **Excel Skills for Business: Intermediate I — Macquarie University**, October 26, 2026. Grade: 97%. [Verify credential](https://www.coursera.org/account/accomplishments/verify/8H9Z7YHEIQM1).

- **Financial Markets — Yale University**, October 26, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/7THDQFV7J51T).
- **Accounting Analysis II: Accounting for Liabilities and Equity — University of Illinois Urbana-Champaign**, October 26, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/7NVRK3BEG2HO).
- **Accounting Analysis II: Measurement and Disclosure of Liabilities — University of Illinois Urbana-Champaign**, October 26, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/TAMGVW746H14).
- **Introduction to Microsoft Excel — Coursera**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/51R9P2JU5MZF).
- **Project and Stress-Test Financial Plans — Coursera**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/UHTYEDOV79MG).
- **Financial Ratios: Analyze & Apply Key Metrics — Coursera**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/JRCQ8OXKJUCY).
- **Accounting Analysis I: Measurement and Disclosure of Assets — University of Illinois Urbana-Champaign**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/LQMAWAKK7TIJ).
- **SOX Compliance and Corporate Governance — EDUCBA**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/00J90TJZ299M).
- **Cost Accounting: Decision Making — Technical University of Munich (TUM)**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/8MV907JA3RBW).
- **Working Capital and Cash Management Essentials — EDUCBA**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/ETR2BYCHOL04).
- **Cost Accounting: Profit and Loss Calculation — Technical University of Munich (TUM)**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/W2XAE7ZX9SZY).
- **Basics of Cost Accounting: Product Costing — Technical University of Munich (TUM)**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/N6DGMA141F3Z).
- **Accounting Analysis I: The Role of Accounting as an Information System — University of Illinois Urbana-Champaign**, October 25, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/FFZYQZZPGX14).
- **Advanced Financial Planning for Forecasting and Valuation** — John Wiley & Sons · Completed October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/SPVNC91V1JPI).
- **Performance Management and Strategic Planning in Finance** — John Wiley & Sons · Completed October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/9ZP4KUWJKM79).
- **Master Financial Budgeting and Forecasting** — EDUCBA · Completed October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/R1LKRIJCA3J2).
- **Boost FP&A Variance Analysis with Copilot** — Completed October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/YPJLWFDFPIYN).
- **Foundations of Financial Analysis and Business Performance** — John Wiley & Sons · Completed October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/UD3N08634LZS).
- **Corporate & Business Strategy** — Corporate Finance Institute · Completed October 24, 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/4AGHY0CAQM7L).
- **Financial Analysis Fundamentals** — Corporate Finance Institute · Completed October 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/6XS7MXROJK38).
- **Reading Financial Statements** — Corporate Finance Institute · Completed October 24, 2026. [Verify credential](https://coursera.org/verify/UH4WOC2M0JOD).
- **Operational Modeling** — Corporate Finance Institute · Completed October 24, 2026. [Verify credential](https://coursera.org/verify/N3WXVFCPBXUX).
- **Create a Financial Statement using Microsoft Excel** — Completed October 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/KHBT5PT2DULE).
- **Create Charts and Dashboards Using Microsoft Excel** — Completed October 2026. [Verify credential](https://www.coursera.org/account/accomplishments/verify/2S916JBQ7560).
- **Fundamentals of Quantitative Modeling** — University of Pennsylvania · Completed October 24, 2026. [Verify credential](https://coursera.org/verify/PVXB3VOVO4EK).
- **SQL for Data Science** — University of California, Davis · Completed October 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/ENZPC7RHRZ5L).
- **Power BI Masterclass 8 - Python, Finance, and Advanced DAX** — Packt · Completed October 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/63HT1Z2VSU9B).
- **Project Execution: Running the Project** — Google · Completed October 24, 2026. [Verify credential](https://coursera.org/verify/HN80SZTAZNV9).
- **FinTech Law and Policy** — Duke University · Completed October 23, 2026. [Verify credential](https://coursera.org/verify/85Z820Z3JO6N).
- **FP&A Modeling: Variance Analysis & Forecasting** — IBM · Completed October 23, 2026. [Verify credential](https://coursera.org/verify/5N2ODALI7T2H).
- **AI for Data Analysis** — Google · Issued October 2026 · Expires January 2036 · Credential ID: 7NMYU729VOSW. [Verify credential](https://www.coursera.org/account/accomplishments/records/7NMYU729VOSW).
- **Introduction to Agents — Certificate of Recognition** — Mercor Academy · AI agent evaluation, rigor, calibration, and clarity | OCT 15, 2026.
- **Financial Planning & Analysis (FP&A): Foundations** — IBM · Course certificate | OCT 2026. [Verify credential](https://www.coursera.org/account/accomplishments/records/2RFBQ5DUJR1N).
- **Emergency Medical Tech-Basic** — Lincoln Land Community College · Certificate of Completion | MAY 2011.
- **Fire Prevention Principles** — Lincoln Land Community College · Certificate of Completion | DEC 2011.
- **Vehicle/Machinery Operations** — Lincoln Land Community College · Certificate of Completion | MAY 2012.
- **Technical Rescue Awareness** — Lincoln Land Community College · Certificate of Completion | JUL 2012.

The specialization and certificate lists expand as additional credentials are completed and verified.

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




