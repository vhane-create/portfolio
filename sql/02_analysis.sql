-- Aggregate actuals BEFORE joining to budget to avoid multiplying plan values.
-- Include keys from both sources so actual-only categories remain visible.
CREATE VIEW monthly_variance AS
WITH actuals AS (
 SELECT month, category_id, SUM(amount) AS actual, COUNT(*) AS transaction_count
 FROM transactions GROUP BY month, category_id
), keys AS (
 SELECT month, category_id FROM budgets
 UNION SELECT month, category_id FROM actuals
), joined AS (
 SELECT k.month, c.category_name, c.category_type, b.amount AS budget,
        a.actual, COALESCE(a.transaction_count,0) AS transaction_count
 FROM keys k
 JOIN categories c ON c.category_id=k.category_id
 LEFT JOIN budgets b ON b.month=k.month AND b.category_id=k.category_id
 LEFT JOIN actuals a ON a.month=k.month AND a.category_id=k.category_id
)
SELECT *, actual-budget AS variance,
 ROUND(100.0*(actual-budget)/NULLIF(budget,0),1) AS variance_pct,
 CASE WHEN budget IS NULL THEN 'Missing budget'
      WHEN actual IS NULL THEN 'Missing actuals'
      WHEN actual=budget THEN 'On budget'
      WHEN (category_type='Revenue' AND actual>budget)
        OR (category_type='Expense' AND actual<budget) THEN 'Favorable'
      ELSE 'Unfavorable' END AS assessment,
 CASE WHEN category_type='Revenue' THEN actual-budget
      ELSE budget-actual END AS profit_impact
FROM joined;

-- Result 1: category variances (raw dollar variance = actual minus budget).
SELECT month, category_name, budget, actual, variance, variance_pct, assessment
FROM monthly_variance ORDER BY month, category_type DESC, category_name;

-- Result 2: operating profit; incomplete sources produce unavailable results.
SELECT month,
 CASE WHEN COUNT(budget)=COUNT(*) THEN
   SUM(CASE WHEN category_type='Revenue' THEN budget ELSE -budget END)
 END AS budget_profit,
 CASE WHEN COUNT(actual)=COUNT(*) THEN
   SUM(CASE WHEN category_type='Revenue' THEN actual ELSE -actual END)
 END AS actual_profit,
 CASE WHEN COUNT(profit_impact)=COUNT(*) THEN SUM(profit_impact)
 END AS profit_variance
FROM monthly_variance GROUP BY month;

-- Result 3: rank unfavorable contributors using a window function.
WITH adverse AS (
 SELECT month, category_name, -profit_impact AS shortfall
 FROM monthly_variance WHERE profit_impact<0
)
SELECT month, category_name, shortfall,
 DENSE_RANK() OVER(PARTITION BY month ORDER BY shortfall DESC) AS impact_rank,
 ROUND(100.0*shortfall/SUM(shortfall) OVER(PARTITION BY month),1) AS adverse_share_pct
FROM adverse ORDER BY month, impact_rank, category_name;
