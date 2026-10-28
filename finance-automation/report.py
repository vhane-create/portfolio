"""Synthetic enterprise FP&A reporting pipeline; Python 3.10+, standard library only.
Run: python finance-automation/report.py
Outputs finance-automation/output/variance_report.csv and executive_summary.txt.
No employer or customer information is used.
"""
from pathlib import Path
import csv
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "synthetic_actuals.csv"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
required = {"period", "department", "account", "budget", "actual"}

def load():
    with INPUT.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("Missing required finance fields")
        rows = []
        for row in reader:
            budget, actual = float(row["budget"]), float(row["actual"])
            if budget < 0 or actual < 0:
                raise ValueError("Expected nonnegative expense data")
            rows.append({**row, "budget": budget, "actual": actual,
                         "variance": actual-budget,
                         "variance_pct": (actual-budget)/budget if budget else None})
    if not rows: raise ValueError("No rows")
    return rows

def main():
    rows = load()
    with (OUT/"variance_report.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.writer(fh);w.writerow(["period","department","account","budget","actual","unfavorable_variance","variance_pct"])
        for r in rows:
            w.writerow([r["period"],r["department"],r["account"],r["budget"],r["actual"],round(r["variance"],2),
                        "" if r["variance_pct"] is None else round(r["variance_pct"],4)])
    totals=defaultdict(lambda:[0.,0.])
    for r in rows:
        totals[r["department"]][0]+=r["budget"]
        totals[r["department"]][1]+=r["actual"]
    total_budget=sum(r["budget"] for r in rows)
    total_actual=sum(r["actual"] for r in rows)
    lines=["SYNTHETIC FP&A EXECUTIVE REPORT","All dollar amounts are simulated expenses.",
           f"Total budget: ${total_budget:,.0f}",f"Total actual: ${total_actual:,.0f}",
           f"Unfavorable variance: ${total_actual-total_budget:,.0f}",
           "DEPARTMENT ANALYSIS"]
    for name,(b,a) in sorted(totals.items(),key=lambda kv:kv[1][1]-kv[1][0],reverse=True):
        lines.append(f"{name}: budget ${b:,.0f}; actual ${a:,.0f}; unfavorable variance ${a-b:,.0f}")
    (OUT/"executive_summary.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    assert abs(sum(v[0] for v in totals.values())-total_budget)<.01
    assert abs(sum(v[1] for v in totals.values())-total_actual)<.01
    print("\n".join(lines))

if __name__=="__main__": main()
