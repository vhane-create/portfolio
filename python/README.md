# Python FP&A Variance Analysis

A reproducible, **standard-library-only Python** companion to the Excel and SQL budget-versus-actual projects.

**Business question:** Which categories explain the operating-profit shortfall?

**Run:** `python3 python/fpa_variance_analysis.py` from the repository root.

**Demonstrates:** CSV parsing, financial calculations, favorable/unfavorable logic, variance percentages, reusable functions, and assertions that reconcile the result to the companion Excel and SQL case studies.

**Expected results:** Budgeted operating profit $35,000; actual operating profit $24,000; unfavorable difference $11,000.

**Data provenance:** Entirely simulated portfolio figures, not real company, client, or salon financial data. No external dependencies or credentials required.

**Codex workflow:** This project is suitable for AI-assisted refactoring, test generation, and documentation review. All generated calculations should be checked against the documented Excel and SQL baseline; this repository does not assert an unverified tool execution history.
