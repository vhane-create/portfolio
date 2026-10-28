"""Regression checks for the synthetic FP&A reporting workflow.
Run from repository root: python -m unittest discover -s finance-automation -p 'test_*.py'
"""
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class ReportingTests(unittest.TestCase):
    def test_input_schema_and_reconciliation(self):
        with (ROOT / "synthetic_actuals.csv").open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(float(r["budget"]) >= 0 and float(r["actual"]) >= 0 for r in rows))
        budget = sum(float(r["budget"]) for r in rows)
        actual = sum(float(r["actual"]) for r in rows)
        variance = sum(float(r["actual"]) - float(r["budget"]) for r in rows)
        self.assertAlmostEqual(variance, actual-budget, places=5)

    def test_report_outputs(self):
        run = subprocess.run([sys.executable, str(ROOT / "report.py")],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertIn("SYNTHETIC FP&A EXECUTIVE REPORT", run.stdout)
        self.assertTrue((ROOT / "output" / "variance_report.csv").exists())
        self.assertTrue((ROOT / "output" / "executive_summary.txt").exists())
        with (ROOT / "output" / "variance_report.csv").open(newline="", encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 16)

if __name__ == "__main__":
    unittest.main()
