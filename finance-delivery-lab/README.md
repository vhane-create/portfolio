# Finance Delivery Performance Lab

[Open live demo](https://vhane-create.github.io/portfolio/finance-delivery-lab/)

## Employer questions this answers
- **Can you deliver under a deadline?** Set a target and run a timed, reproducible financial reporting batch. This is a benchmark, not proof of past work deadlines.
- **Can you deliver accurately?** Five independent validation checks must pass before the CSV export is enabled.
- **Can you explain the result?** The app generates an executive brief identifying variance and a cost center to investigate.
- **Can you automate repetitive work?** It generates synthetic records, aggregates them, validates totals, and creates a report and CSV without manually copying figures.
- **Can I inspect the method?** All logic is readable in index.html and uses no paid services or external dependencies.

## How to use
Choose 1,000, 10,000, or 50,000 transactions; choose a repeatable seed; set a deadline target in milliseconds; click **Run reporting workflow**. The browser measures the processing using performance.now(). Review the reconciled totals and QA log; export the CSV if all checks pass.

## Synthetic model
For each row, a deterministic seeded pseudorandom generator chooses one of five cost centers, a budget from $100 to $5,000, and a delta from −$500 to +$700. Actual = budget + delta. An anomaly is flagged when absolute row variance exceeds $450.

## Validation
1. Group counts equal generated row count.
2. Sum of grouped budgets equals the independently accumulated source budget.
3. Sum of grouped actuals equals the independently accumulated source actual.
4. Sum of grouped variances equals source actual minus source budget.
5. All budget and actual totals are nonnegative.

**Acceptance checks:** run twice with identical seed and count; the financial totals should match (timings may differ). Change the seed; totals should generally change. Try 1,000 and 50,000 records. Set a 1ms deadline; the app reports whether it meets the target rather than claiming a guaranteed speed. Exported CSV should reconcile with the screen.

## Important limits
All figures are simulated; no company data or private information is collected. This browser demo measures client-side generation, grouping and validation, not network transfer, ERP ingestion, database throughput, production SLAs, or prior Mercor performance. Timings vary by hardware, browser and load. The generated management recommendation is a rule-based summary, not a live AI model.
