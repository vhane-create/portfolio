"""Reproducible FP&A variance analysis using simulated portfolio data.

Run: python3 python/fpa_variance_analysis.py
Standard library only. Illustrative data; not employer results.
"""
import csv
from io import StringIO

DATA = """category,budget,actual,type
Revenue,100000,95000,revenue
Payroll,40000,43000,expense
Supplies,15000,18000,expense
Rent,10000,10000,expense
"""

def analyze(rows):
    report = []
    for row in rows:
        budget, actual = float(row["budget"]), float(row["actual"])
        variance = actual - budget
        favorable = variance >= 0 if row["type"] == "revenue" else variance <= 0
        report.append({
            "category": row["category"], "budget": budget, "actual": actual,
            "variance": variance, "variance_pct": variance / budget * 100 if budget else None,
            "assessment": "Favorable" if favorable else "Unfavorable"
        })
    return report

def operating_profit(report):
    revenues = [r for r in report if r["category"] == "Revenue"]
    expenses = [r for r in report if r["category"] != "Revenue"]
    return (sum(r["budget"] for r in revenues) - sum(r["budget"] for r in expenses),
            sum(r["actual"] for r in revenues) - sum(r["actual"] for r in expenses))

if __name__ == "__main__":
    rows = list(csv.DictReader(StringIO(DATA)))
    report = analyze(rows)
    budget_profit, actual_profit = operating_profit(report)
    assert (budget_profit, actual_profit) == (35000, 24000)
    assert actual_profit - budget_profit == -11000
    print("PERSONAL PORTFOLIO SIMULATION — FP&A VARIANCE REPORT")
    for r in report:
        print(f'{r["category"]:10} Budget: ${r["budget"]:,.0f}  Actual: ${r["actual"]:,.0f}  Variance: ${r["variance"]:+,.0f}  {r["assessment"]}')
    print(f"Operating profit: budget ${budget_profit:,.0f}, actual ${actual_profit:,.0f}")
    print(f"Profit variance: ${actual_profit - budget_profit:+,.0f} (unfavorable)")
