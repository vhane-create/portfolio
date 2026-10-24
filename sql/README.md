# SQL financial variance analysis

Vannetta Haney portfolio sample. All records are simulated; October 2026 is an illustrative reporting month. USD. Payroll, supplies and rent are assumed to be all operating expenses. This is a practice project, not employer or client work.

## Run locally

Use SQLite 3.25 or newer and a new database:

```
sqlite3 finance.db < 01_setup.sql
sqlite3 -header -column finance.db < 02_analysis.sql
sqlite3 -header -column finance.db < 03_checks.sql
```

Run setup and analysis once per new database. The analysis script creates a reusable `monthly_variance` view and prints three reports. The checks script should return no rows. SQLite reports constraint violations for duplicate transaction IDs, invalid categories, or negative amounts.

## Method

Actual transactions are aggregated by month and category before joining to the budget, preventing the budget from being duplicated for multiple transactions. A union of source keys retains actual-only and budget-only categories. Missing data stays NULL, zero budget returns NULL for variance percentage, and explicit zero actuals remain valid. Missing sources are flagged and block a complete operating-profit result.

Dollar variance is actual minus budget. Profit impact reverses the sign for expenses. Revenue above budget and expenses below budget are favorable. Percentage variance uses budget as the denominator. DENSE_RANK and a partitioned SUM rank adverse contributors and calculate their shares.

## Verified sample results

| Category | Budget | Actual | Variance | Variance % |
|---|---:|---:|---:|---:|
| Revenue | 100000 | 95000 | -5000 | -5.0 |
| Payroll | 40000 | 43000 | 3000 | 7.5 |
| Supplies | 15000 | 18000 | 3000 | 20.0 |
| Rent | 10000 | 10000 | 0 | 0.0 |

Budgeted operating profit is $35,000; actual profit is $24,000; variance is -$11,000. Adverse contributions are revenue $5,000 (45.5%), payroll $3,000 (27.3%) and supplies $3,000 (27.3%). Shares may sum to 100.1% due to rounding.

Results establish the size of the variances, not their causes. Follow up with revenue-detail reconciliation and payroll hours/rates and supply quantities/prices.

## Verification

Executed with Python's SQLite engine. Assertions covered expected totals, duplicate key rejection, missing actuals, explicit zero actuals, zero budget, actual-only categories and source-to-report reconciliation. CSV files contain baseline report outputs.
