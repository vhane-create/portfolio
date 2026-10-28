-- Synthetic enterprise spend analysis. Compatible with SQLite 3.
-- Import synthetic_actuals.csv into expense_actuals(period, department, account, budget, actual).
-- Expenses: positive actual-budget is unfavorable.
SELECT period, department,
       ROUND(SUM(budget),2) AS budget,
       ROUND(SUM(actual),2) AS actual,
       ROUND(SUM(actual-budget),2) AS unfavorable_variance,
       ROUND(100.0*SUM(actual-budget)/NULLIF(SUM(budget),0),2) AS variance_pct
FROM expense_actuals
GROUP BY period, department
ORDER BY period, unfavorable_variance DESC;

-- Identify material overspend by account.
SELECT period, department, account,
       ROUND(actual-budget,2) AS unfavorable_variance
FROM expense_actuals
WHERE actual-budget > 10000
ORDER BY unfavorable_variance DESC;

-- Reconciliation check: detail sums should match summary.
SELECT ROUND(SUM(budget),2) AS total_budget,
       ROUND(SUM(actual),2) AS total_actual,
       ROUND(SUM(actual-budget),2) AS unfavorable_variance
FROM expense_actuals;
