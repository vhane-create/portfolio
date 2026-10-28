# Executive FP&A Portfolio | Investment Committee Case Study

**Author:** Vannetta Haney  
**Audience:** CFO, Finance VP, Investment Committee  
**Case:** Hypothetical five-year capacity expansion; all inputs simulated  
**Live interactive case:** [Enterprise Finance Decision Lab](../decision-lab/)  
**Model documentation:** [Decision Lab README](../decision-lab/README.md)

## Executive decision
The proposed expansion should be evaluated on **incremental, unlevered free cash flow**, not accounting revenue alone. The live model estimates NPV and IRR, discounts cash flows at an editable WACC, and stress-tests the decision. **No unconditional approval is asserted:** approval depends on the selected scenario and verified assumptions.

## Decision drivers
1. **Volume and price realization:** Sales growth is an editable proxy for incremental demand. The model does not separately estimate unit volume and price.
2. **Contribution economics:** Margin directly influences operating cash generation. Margin compression is a key downside risk.
3. **Cost discipline:** Fixed costs reduce EBITDA and can change the investment conclusion.
4. **Capital intensity:** Up-front capex and working capital consumption can offset profitable operations.
5. **Cost of capital:** Higher WACC reduces the value of later cash inflows.

## Recommended management questions
- Is the year-one revenue assumption supported by committed demand or credible pipeline evidence?
- Can the company achieve modeled contribution margin without additional overhead or maintenance capex?
- Are working-capital assumptions supported by historical cash conversion?
- What is the downside action plan if the project misses its first-year revenue target?
- Does the investment outperform alternative uses of capital?

## Decision framework
- **Positive NPV:** Advance to diligence, validate the demand forecast, and assess execution capacity.
- **Negative NPV:** Reject or redesign the investment under current assumptions.
- **IRR:** Use as a supporting metric; do not substitute IRR for NPV when comparing investments of different size.
- **Discounted payback:** Use as a supplementary liquidity metric, not the primary value criterion.
- **Risk:** Review deterministic downside cases and sensitivities; these are not probability-weighted expected outcomes.

## Controls and limitations
The model assumes five years of straight-line depreciation, no salvage value, simplified cash taxes, and full year-five release of working capital. It excludes debt financing, maintenance capex, tax-loss carryforwards, and detailed tax timing. It is a portfolio exercise, **not** an employer engagement, real client analysis, or investment recommendation.

## Related evidence
- [Three-year integrated Excel forecast documentation](../integrated-forecast/)
- [Python/SQL variance reporting workflow](../finance-automation/)
- [Portfolio homepage](../)

## Interview walkthrough (5 minutes)
1. Explain the business question and why NPV is the primary decision metric.
2. Show the base case, then lower year-one revenue and contribution margin.
3. Discuss working-capital effects and the year-five cash release.
4. Demonstrate how the investment conclusion changes under a higher WACC.
5. Close with diligence requirements and limitations instead of overstating precision.
