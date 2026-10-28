# Finance flagship calculation verification

Verification date: 2026-10-28.

## Scope and method

Read the current `index.html` for each of six flagship applications directly from the GitHub repository. Extracted the pure `calculate(v)` function and executed it using its documented default inputs in an isolated JavaScript evaluation. Inspected the returned model control status and verified all displayed numeric metrics and line items were finite.

**This was a calculation-level smoke test, not a browser UI test or a confirmed GitHub Actions CI run.** It does not validate the rendering, reset button, print feature, cross-browser behavior, deployment status, or accounting completeness.

| Model | Observed outputs | Control status |
|---|---|---|
| Integrated Three-Statement Forecast | Revenue 129.60; net income 29.145; ending cash 39.0907534 | PASS: balance sheet control |
| Global Consolidation | Revenue 131.50; expense 92.20; operating profit 39.30 | PASS: elimination check |
| Workforce Planning | Ending headcount 227.4; average FTE 223.7; loaded cost 28,289,996.80 | PASS: assumption checks |
| Financial Controls | Difference 1,000; threshold 2,500; exceptions 0 | PASS: reconciliation, approval and evidence |
| Treasury & Liquidity | Week 13 cash 7.55; floor 8.00; funding gap 0.45 | REVIEW REQUIRED: correctly detects breach of liquidity floor |
| Enterprise Data Pipeline | Valid records 9,700; exceptions 300; revenue 3,152,500 | PASS: source row count reconciliation |

All six models returned finite numbers for their default scenarios. **The Treasury REVIEW REQUIRED result is expected and correct**, not a failed test.

## Important model limitations

- The three-statement model uses a simplified single-period balance sheet and assumes opening non-cash fixed assets and other liabilities are zero.
- The consolidation model is a simplified operating view and is not a complete accounting consolidation.
- Workforce planning uses average-FTE approximations, not employee-level payroll.
- SOX control checks are illustrative, not evidence of actual SOX certification or a completed audit.
- Treasury assumes constant weekly flows; it does not include bank facilities, covenant schedules, or seasonal payment timing.
- The data pipeline is a mathematical exception-rate simulation, **not actual row-by-row ETL**.

## Remaining acceptance criteria

1. Confirm GitHub Actions regression workflow completes successfully.
2. Open each published page in a browser and test inputs, reset and print controls.
3. Test negative, missing, out-of-range and boundary inputs.
4. Independently review accounting assumptions and model formulas before labeling any model production-ready.
5. Record screenshots or exported reports only after checking values against the model.

No historical employer performance, client metrics, or production claims are inferred from these tests.
