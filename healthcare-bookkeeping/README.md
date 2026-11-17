# Healthcare Bookkeeping & Month-End Close
Enterprise-scale healthcare bookkeeping flagship for Vannetta Haney's portfolio.

[Open the flagship](https://vhane-create.github.io/portfolio/healthcare-bookkeeping/)

## Scope
A fictional national healthcare network with $65M monthly net service revenue, 2.4M modeled annual unique patients, 400,000 November encounters, 480 locations and 5,000 employees. Population assumptions describe the network; the delivered data is aggregate financial posting batches and four receivable pools, not millions of individual patient records. No real patient data is included.

## Reviewer walkthrough
1. Review the completed income statement, balance sheet and cash flow.
2. Inspect the bank reconciliation and patient/insurance aging pools.
3. Open “Inspect or omit month-end adjustments.” Omit contractual revenue adjustments: the trial balance still balances, while receivables differ from independent subledger evidence by $25M.
4. Omit bank entries: book cash exceeds adjusted bank by $50,000.
5. Omit payroll: profit increases $3.5M without improving cash. A complete close requires every adjustment group even when arithmetic checks tie.
6. Restore baseline, change payroll or ending supplies and trace the statements. Export the active journal, trial balance or financial statements to CSV.

## Deliverables
- `index.html`, `style.css`, `app.mjs`: responsive interactive review workspace; no build dependencies.
- `model.mjs`: shared double-entry accounting model.
- `model.test.mjs`: independent baseline checks, all 128 posting combinations, estimate changes, valid zero inputs and invalid-input rejection.
- `source-register.csv`: synthetic evidence and accounting treatment.
- `journal.csv`, `trial-balance.csv`, `receivables.csv`, `bank-reconciliation.csv`, `financial-statements.csv`: fixed baseline records for Excel or other analytical tools.
- `close-checklist.csv`: baseline posting state plus blank human preparer/reviewer fields.
- `case-study.md`: accounting judgments, working-capital bridge and management actions.
- `build-downloads.mjs`: regenerate baseline CSV files from the model.

## Reproduction
Serve this folder with an HTTP server to load ES modules. No API key or external services are needed.

```sh
node model.test.mjs
node build-downloads.mjs
```

The base case has $21.55M income before tax, $45.15M ending cash, $135.05M assets, $37.5M liabilities and $97.55M equity. Operating cash is $15.15M. All six reconciliation differences are zero.

Downloadable CSV files are labeled baseline. Browser export buttons reflect active assumptions and selected adjustment groups. Printing includes all workspace panels. Inputs do not persist after a reload.

## Attribution
Project direction: Vannetta Haney. Web, model and documentation developed with Codex assistance. All company names and financial evidence are fictional. This is an illustrative portfolio case, not employer results or audited financial reporting.
