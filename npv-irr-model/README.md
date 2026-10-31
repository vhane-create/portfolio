# Financial Modeling with NPV and IRR

[Live flagship](https://vhane-create.github.io/portfolio/npv-irr-model/) · [Excel workbook](Vannetta_Haney_NPV_IRR_Financial_Model.xlsx) · [Portfolio](https://vhane-create.github.io/portfolio/)

## Investment decision

Evaluate a fictional five-year operating automation investment using incremental unlevered cash flow. The project demonstrates investment appraisal, financial modeling, scenario analysis and capital allocation. It is a personal portfolio simulation with Codex-assisted implementation, not an employer deliverable or an earned certification.

The base case commits $750,000 of initial capital expenditure and $52,000 of initial working capital. At a 12% annual hurdle rate, modeled NPV is **$63,697**, IRR is **14.8%**, and undiscounted cash is recovered at the end of Year 4. The initial cash outlay is $802,000, not just the capex amount.

| Case | NPV at 12% | Annual IRR | First recovered year-end |
| --- | ---: | ---: | --- |
| Base | $63,697 | 14.8% | Year 4 |
| Downside | ($354,711) | -4.6% | Not within five years |
| Upside | $414,376 | 28.7% | Year 3 |

### Management interpretation

The base investment clears the hurdle with limited headroom. Increasing the hurdle to 16% reduces base NPV to approximately **($25,690)**. At the 12% hurdle, reducing the revenue level to 90% of base produces approximately **($39,230)** of NPV. Validate revenue realization, implementation capacity, operating margin and vendor quotes before committing capital. These are findings from hypothetical inputs, not real business outcomes.

## Deliverables

- **Excel:** three linked worksheets. Investment Review presents the decision metrics, editable native chart, cash flows and terminal review checks. Assumptions owns one case selector, case drivers, common inputs and a native two-input What-If Data Table. Cash Flows owns the operating and cash calculations.
- **Interactive model:** case selection, editable drivers, NPV and IRR, year-end payback, profitability index, cash flow chart, NPV curve and CSV export. Invalid or blank inputs hide the results and show the missing input.
- **Reproducible source:** `model.js` contains the financial engine. `model.test.js` verifies timing, cash flow reconciliation, scenarios, input changes and boundary conditions without external dependencies.
- **Baseline outputs:** `baseline-scenarios.csv` and `base-cash-flows.csv` record the original simulation. The website recalculates rather than displaying these static files.

## Assumptions

All values are USD. Periods are annual and equally spaced. Year 0 is immediate; Years 1-5 are year-end. There are no actual historical financial results in this example.

| Driver | Base | Downside | Upside |
| --- | ---: | ---: | ---: |
| Year 1 revenue | $520,000 | $440,000 | $600,000 |
| Annual revenue growth | 8% | 3% | 12% |
| Gross margin | 65% | 60% | 68% |
| Year 1 operating cost | $100,000 | $115,000 | $95,000 |
| Initial capital expenditure | $750,000 | $825,000 | $725,000 |
| Year 5 gross disposal proceeds | $100,000 | $75,000 | $120,000 |

Common editable inputs: 12% discount rate, 25% cash tax rate, $30,000 annual maintenance capex, working capital equal to 10% of revenue, 3% annual operating cost growth, and 1.0x revenue multiplier. The web model exposes revenue directly; Excel's additional revenue multiplier drives its native sensitivity table.

## Calculation logic

1. Revenue grows from Year 1 using the annual growth driver. Gross profit is revenue multiplied by gross margin.
2. EBITDA equals gross profit less operating cost. Initial capex depreciates straight-line to zero over five years.
3. EBIT equals EBITDA less depreciation. Cash taxes equal positive EBIT multiplied by the tax rate. Losses receive no immediate cash tax benefit.
4. Operating cash flow equals EBIT less cash taxes plus depreciation. Maintenance capex is deducted as cash.
5. Initial working capital funds Year 1. Later annual changes are cash investments or releases. All remaining working capital is recovered at the end of Year 5.
6. Disposal proceeds are taxed at the tax rate because the initial asset has zero closing book value. No perpetuity value is added.
7. Year 0 free cash flow is negative capex less initial working capital. Annual free cash flow equals operating cash flow less maintenance capex and working capital increases, plus final recovery and after-tax disposal proceeds when applicable.
8. NPV discounts Years 1-5 and adds Year 0 once. Excel: `=NPV(rate,CF1:CF5)+CF0`. IRR includes the entire periodic series, `=IRR(CF0:CF5)`.
9. Profitability index is the present value of future net cash flows divided by the positive initial outlay. Payback is the first year-end where cumulative nominal cash is nonnegative; it is not discounted payback or a fractional-year estimate.

### Model boundaries

This finite-life project excludes debt, interest, financing fees, perpetuity value, tax-loss carryforwards and additional tax depreciation from maintenance capex. Maintenance is a cash-only reinvestment requirement in this simplified model. Validate those items before adapting it to a real investment.

IRR is shown only for one initial outflow followed by nonnegative cash inflows with at least one positive inflow. It may be negative. The web model returns unavailable for nonconventional cash flows rather than selecting one of potentially multiple roots. NPV remains available. Payback and IRR do not replace the dollar-value decision from NPV.

## Excel instructions

Open `Vannetta_Haney_NPV_IRR_Financial_Model.xlsx` in Microsoft Excel with automatic calculation enabled. Choose 1, 2 or 3 in `Assumptions!D5` for Base, Downside or Upside. Edit the blue source inputs. The active driver rows feed the same cash flow build in every case. Blank selected case inputs become unavailable; blank unselected cases do not block the current case.

The native sensitivity table varies revenue multiplier `Assumptions!D45` across columns and discount rate `Assumptions!D40` down rows. Both are real inputs to the model. `Assumptions!J12` reproduces base NPV at 1.0x revenue and 12% discount. The table is evaluated for whichever operating case is selected. Use automatic calculation including data tables; recalculate after editing. A third-party spreadsheet viewer may show cached values instead of refreshing this Excel feature.

Workbook construction checks independently reconciled all three scenarios with the JavaScript engine, verified base and non-base sensitivity cells, tested missing selected versus unselected inputs, checked NPV against summed present values, checked NPV at IRR, and reconciled working capital. All checks passed in the authoring engine. Native desktop Excel was not available for an additional open-and-recalculate test.

## Reproduce and test

No dependencies or paid service are required for the website or financial engine.

```sh
node --test npv-irr-model/model.test.js
```

From this folder, use `node --test model.test.js`. Serve the repository with any static HTTP server and open `/npv-irr-model/`. Browser modules require HTTP; opening `index.html` directly from a local file may be blocked.

## Formula references

- [Microsoft NPV function](https://support.microsoft.com/en-us/excel/functions/npv-function)
- [Microsoft IRR function](https://support.microsoft.com/en-us/excel/functions/irr-function)

These references establish formula conventions. They are not sources for the fictional investment assumptions.
