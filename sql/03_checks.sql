-- Each diagnostic returns zero rows when no issues are found.
SELECT month, category_name, assessment FROM monthly_variance
WHERE budget IS NULL OR actual IS NULL;
SELECT transaction_id, COUNT(*) AS duplicates FROM transactions
GROUP BY transaction_id HAVING COUNT(*)>1;
SELECT t.transaction_id FROM transactions t
LEFT JOIN categories c ON c.category_id=t.category_id
WHERE c.category_id IS NULL;
-- Independent reconciliation of raw actuals to aggregated analysis.
SELECT t.month, SUM(t.amount) - (
 SELECT SUM(v.actual) FROM monthly_variance v WHERE v.month=t.month
) AS difference
FROM transactions t GROUP BY t.month
HAVING ABS(difference)>0.005;
