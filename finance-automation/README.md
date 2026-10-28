# Automated Finance Reporting | Python + SQL

An auditable, reproducible **synthetic enterprise expense variance reporting** demonstration for a Senior FP&A technical portfolio.

## Run
From the repository root:
```bash
python finance-automation/report.py
```
This creates `finance-automation/output/variance_report.csv` and `executive_summary.txt`. The script uses only the Python standard library. Input CSV is committed for reproducibility.

## SQL
`analysis.sql` contains department-period budget variance reporting, material overspend detection, and reconciliation. Import `synthetic_actuals.csv` as a SQLite table named `expense_actuals` with columns `period TEXT, department TEXT, account TEXT, budget REAL, actual REAL`.

## Controls
- Validates required fields and nonnegative expense amounts.
- Reports zero-budget percentage variances as blank rather than dividing by zero.
- Reconciles departmental totals with detailed data.
- Distinguishes **unfavorable** cost variance (actual minus budget) from favorable underspend.
- All data is simulated; no employer data.

## Portfolio connection
This is a separate, executable automation workflow complementing the interactive [Enterprise Finance Decision Lab](../decision-lab/) and [integrated Excel forecast](../integrated-forecast/). It is **not yet** a single connected application with the web decision lab.
