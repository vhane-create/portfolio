# Accounting Close & Financial Reporting

A complete synthetic October 2026 accounting case for Vannetta Haney’s portfolio. It connects journal entries, adjustment evidence, unadjusted and adjusted trial balances, FIFO manufacturing costs, bank reconciliation, and three linked financial statements.

## Reviewer walkthrough

1. Open `index.html` through a local HTTP server or the portfolio page.
2. Select **Show unadjusted books**, then inspect why a balanced trial balance is not enough.
3. Record all adjustments. Trace A01–A08 into the journal and adjusted account balances.
4. Omit depreciation and observe the $800 profit/net-asset overstatement even though the arithmetic checks still tie.
5. Omit bank adjustments or the overhead close and inspect the relevant failed reconciliation.
6. Change the wage accrual, receivables allowance or bank fee. Export the resulting journal CSV.
7. Download the formula-driven Excel workbook and read `accounting-memo.md` for the baseline judgments and cash-versus-profit recommendation.

## Baseline controls

- Revenue $47,000; net income $14,790.
- Ending cash $44,250; total assets $141,990.
- Operating cash flow $1,250; investing cash flow −$6,000; financing cash flow −$1,000.
- Raw materials $13,000; finished goods $7,000; gross receivables $32,000; allowance $960.
- Journal, trial balance, statement equation, direct/indirect cash flow, bank reconciliation, WIP and overhead checks reconcile.

## Workbook

`Vannetta_Haney_Accounting_Close.xlsx` has six worksheets: Statements, Inputs, Costing, Journal, Trial Balance and Reconciliation. Sources and estimates are clearly separated from formulas. Adjustment switches use 1 to record or 0 to omit. The workbook also exposes costing assumptions; changes are hypothetical revisions to the synthetic case. It recalculates linked journal amounts, account balances and statements. No macros or external workbook links.

Web controls cover selected accounting estimates and adjustment groups. The web and workbook share the same baseline case, but only the workbook exposes the additional manufacturing driver inputs. The static memo always describes the baseline.

## Reproduce checks

```
node model.test.mjs
```

Checks assert independent expected baseline balances, all 128 combinations of the seven adjustment groups, omitted-entry consequences, valid zero inputs, changed estimates and invalid-input rejection. Workbook checks independently verify baseline results and actual formula recalculation after changing the allowance and depreciation switch. This is educational accounting, not an audited report or a production general ledger.

## Credentials

- [Financial Reporting Specialization — University of Illinois Urbana-Champaign](https://www.coursera.org/account/accomplishments/specialization/JCRHAUSJIDLP), October 2026.
- [Cost Accounting Specialization — Technical University of Munich](https://www.coursera.org/account/accomplishments/specialization/3TIK9IM7G333), October 2026.

All company names, transactions, source identifiers and financial amounts in this case are fictional. Portfolio direction: Vannetta Haney. Model, workbook and web implementation developed with Codex assistance.

Workbook formulas were evaluated and tested in the generating spreadsheet engine. Native desktop Excel was not available for an additional application-level check. The workbook includes standard scalar Excel formulas and no external links.
