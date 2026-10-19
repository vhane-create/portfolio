# Salon Business Dashboard

[Live dashboard](https://vhane-create.github.io/portfolio/salon-dashboard/)

## Purpose

Explore how appointment volume, average service price, per-visit supplies, and fixed expenses affect two salon locations. Uses synthetic monthly data throughout; figures do not describe actual business performance.

## Direction and implementation

Vannetta Haney selected the business use case, supplied the Springfield, Missouri and Springfield, Illinois locations, and requested a practical portfolio project. Codex implemented the interface, model, validation, export, and tests. Further user review can guide future changes.

## Model

Revenue = whole projected appointments × scenario average price.
Variable expense = projected appointments × supply cost per appointment.
Operating profit = revenue − variable expense − fixed expense.
Margin = profit / revenue, or N/A when revenue is zero.
Break-even visits = ceiling(fixed expense / contribution per visit); not attainable when contribution is zero or negative.

Money is calculated in integer cents. Scenario appointment counts and service prices are rounded before calculating totals. Display cards round dollars for readability; CSV retains cents.

Base sample:
- Missouri: 160 appointments, $95 price, $18 supplies, $5,200 fixed expenses.
- Illinois: 100 appointments, $105 price, $21 supplies, $4,100 fixed expenses.
- Combined revenue $25,700; expenses $14,280; operating profit $11,420.
- Fixed sample budget targets: Missouri revenue $15,000 / profit $7,000; Illinois revenue $11,000 / profit $4,500.

## Validation and assumptions

Required nonnegative numeric inputs; appointments must be whole numbers. Input caps: 2,000 appointments, $2,000 price or per-visit supplies, and $100,000 fixed expenses per month. Scenario changes allow volume from −50% to +50%, and price from −25% to +25%. Invalid inputs pause results and disable export. Losses and prices below supply costs are flagged for review.

This simplified model assumes constant service mix and variable cost per visit. It excludes taxes, financing, and expense categories not entered. No persistence or server requests; reloading resets the sample.

## Verification

Run `node salon-dashboard/model.test.js` from the repository root.

Tests cover known sample totals, scenario math, integer-cent reconciliation, missing/negative/nonfinite values, fractional appointment rejection, zero revenue, operating losses, break-even, and scenario boundaries. A DOM integration check during development confirmed sample rendering, invalid-input handling, reset, scenario updates, and location totals. Full visual browser and device testing remains outstanding.

## Files

- index.html: dashboard and project story
- style.css: responsive layout and presentation
- model.js: pure calculation and validation functions, usable in browser or Node
- app.js: input handling, result rendering, and CSV export
- model.test.js: model regression checks

Open index.html in a browser or serve this directory with a static web server.
