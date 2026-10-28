import unittest
from app import facts,AskRequest
from pydantic import ValidationError
class TestFinance(unittest.TestCase):
 def test_reconciliation(self):
  d=facts();self.assertEqual(d["total_budget"],1690000);self.assertEqual(d["total_actual"],1748000);self.assertEqual(d["total_variance"],58000);self.assertEqual(sum(r["variance"] for r in d["rows"]),58000)
 def test_invalid_input(self):
  with self.assertRaises(ValidationError):AskRequest(question="x")
if __name__=="__main__":unittest.main()

