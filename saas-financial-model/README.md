# SaaS Growth & Retention Model

Personal portfolio simulation for Vannetta Haney, built with Codex assistance. All business data and assumptions are invented; these are not employer or client outcomes.

## Business question

How do acquisition efficiency and customer retention affect recurring revenue, profitability and cash across a 24-month subscription forecast?

Download **Vannetta_Haney_SaaS_Financial_Model.xlsx**, open **Dashboard**, and change **Assumptions!D5** to 1 (Base), 2 (Downside), or 3 (Upside). All blue monthly case inputs are editable. There is one active forecast build. Website case results are static snapshots; use Excel to recalculate edited assumptions.

## Model architecture

- Dashboard: annual results, monthly detail, editable native ARR and cash charts.
- Assumptions: dated Base/Downside/Upside inputs with one Active row for each driver; opening customer, MRR and cash balances.
- Revenue: customer and MRR roll-forwards, revenue timing, ARR and retention metrics.
- Operating: gross profit, cash opex, EBITDA, capex, simplified FCF, cash and unit economics.
- Cohorts: ending MRR by acquisition month, reconciling to the revenue build; annual NRR excludes in-year acquisitions.
- Checks: six terminal reconciliation tests; forecast calculations never depend on checks.
- Guide: methods, review steps, scope and limitations.

## Metric definitions

| Metric | Calculation and scope |
|---|---|
| ARR | Ending MRR × 12; not recognized annual revenue |
| Revenue | Average beginning and ending MRR; changes assumed evenly through month |
| New customers | Acquisition S&M / target CAC, rounded down; full spend remains expensed |
| Realized CAC | Acquisition S&M / matching new customers; same-month attribution, no sales-cycle lag |
| Monthly GRR | (Beginning MRR − churn − contraction) / beginning MRR |
| Monthly NRR | (Beginning MRR − churn + expansion − contraction) / beginning MRR |
| Annual NRR | Year-end MRR of customers present at previous year-end / their opening MRR |
| LTV proxy | New-customer monthly ARPA × gross margin / monthly logo churn; excludes upsell, contraction and discounting |
| CAC payback | Realized CAC / new-customer monthly gross profit; months |
| Annual CAC payback | Annual acquisition S&M / sum of acquired MRR × corresponding gross margin |
| Simplified FCF | EBITDA − cash capex |
| Runway | Positive ending cash / current monthly cash burn; n.a. for cash-generating months |

Expansion and contraction apply to retained MRR after logo churn. Churned customers are fractional expected values; new customer additions are rounded down. All acquisition cohorts share each month's selected retention assumptions. Customer service and customer success are included in the assumed cost of revenue; all S&M is acquisition-related.

## Baseline case results (2028)

| Case | December ARR | Annual NRR | Annual CAC payback | December cash |
|---|---:|---:|---:|---:|
| Base | $3,795,403 | 99.7% | 8.8 months | $1,285,650 |
| Downside | $2,202,790 | 77.4% | 13.4 months | $36,532 |
| Upside | $6,725,345 | 116.4% | 6.5 months | $2,583,359 |

**Interpretation:** in the Downside simulation, ARR growth coincides with a thin cash balance. Investigate acquisition cost, retention and spending together. These results illustrate the supplied assumptions; they are not recommendations for a real company or evidence of past business performance.

## Review exercise

1. Select Downside in Assumptions!D5.
2. Note 2028 annual NRR, CAC payback and cash.
3. Reduce a later-period churn or CAC assumption in the selected case.
4. Trace the change through Revenue, Cohorts and Operating to Dashboard.
5. Confirm the six reconciliation differences remain within 0.01.

## Validation and limitations

The workbook was recalculated and checked in Artifact Tool. All three cases were compared with independent monthly MRR and cash calculations; annual revenue and annual cohort NRR were independently checked. Six reconciliations were reviewed across 24 months and three cases. Input-change tests covered later-period churn, zero churn, zero acquisition spend, and blank selected versus unselected case inputs. No unexpected formula errors remained at export. Native chart bindings, colors and data validation were checked in the saved XLSX. Excel for Mac has not been directly tested.

Cash collections equal recognized revenue; costs are paid in-month. No taxes, debt, financing, interest, D&A, annual prepayment billing, deferred revenue or working-capital changes are modeled. Negative cash is shown without a financing plug. This is a simplified subscription operating model, not a full three-statement model. LTV is a gross-profit approximation, not discounted customer valuation.

Definitions reference: [Stripe, Essential SaaS Metrics](https://stripe.com/resources/more/essential-saas-metrics). No numerical inputs are sourced from Stripe.

## Portfolio description

SaaS financial-modeling simulation with a 24-month forecast, scenario planning, MRR/ARR bridge, cohort retention, acquisition unit economics and cash forecasting; built with Codex assistance.
