# Enterprise Data-to-Decision Pipeline

[Live interactive model](https://vhane-create.github.io/portfolio/enterprise-data-pipeline/)

**Purpose:** ETL validation, duplicate detection, transformations and executive outputs. This is a simulated finance case, not actual employer results.

## Inputs
- Transaction records: 10000
- Average revenue per record USD: 325
- Duplicate rate %: 2
- Missing cost center %: 1
- Average expense per valid record USD: 205
- Variance threshold USD: 100000

## What reviewers can verify
- Adjust any numeric assumption and observe recalculated financial results.
- Inspect the detailed calculated line items.
- Review the built-in validation status and management recommendation.
- Reset the scenario to the documented default assumptions.
- Print the model as an executive brief or save a PDF from the browser.

## Limitations
This is a browser-based teaching and portfolio prototype, not a production ERP, EPM, treasury, audit, or BI platform. It uses no company data, no external API, and no paid service. It does not claim prior employer delivery times or audited financial results. The model is intentionally simplified and requires accounting policy, tax, controls, and data integration review before any real-world deployment.

## Acceptance checks
1. Open the page and confirm all calculated fields are finite numbers.
2. Change one input and confirm at least one dependent result changes.
3. Reset and confirm the original values return.
4. Test an invalid or extreme input and inspect the control status.
5. Print or save the executive brief and confirm its figures match the screen.

## Portfolio relationship
[Main portfolio](../) · [Executive CFO Suite](../executive-cfo-suite/) · [Finance Delivery Performance Lab](../finance-delivery-lab/)
