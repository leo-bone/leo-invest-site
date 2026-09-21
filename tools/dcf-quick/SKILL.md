---
name: dcf-quick
title: DCF Quick — One-Page DCF, Position Sized from the Downside
summary: Give it a ticker and it produces a one-page two-stage DCF range plus a downside floor, then derives the maximum position from the worst case rather than from the size of the opportunity. A quantitative exoskeleton for investing discipline.
read_when:
  - user wants absolute valuation / a DCF, but wants it fast, reproducible and readable on one page
  - user asks what a company is intrinsically worth and whether the margin of safety is enough
  - user wants the worst case settled before deciding position size (sizing from the downside)
  - user mentions "dcf" "discounted cash flow" "intrinsic value" "margin of safety" "position sizing"
---

> **English** · [简体中文](SKILL_CN.md)

# DCF Quick

A reusable skill that has a coding agent run a **simplified two-stage DCF**, and that forces the
production of a **downside floor** and a **position ceiling derived from the worst case**.
Same philosophy as Zara Zhang's `frontend-slides` — reusable, reproducible, verifiable — and
complementary to `valuation-comps`: this skill supplies the absolute anchor, comps the relative one,
and the two cross-check each other.

**This skill runs `scripts/dcf_calc.py` for all arithmetic.** The agent fetches data and sets
assumptions; the script handles discounting, sensitivity, the downside floor and position sizing, so
you don't stack mental-math errors on top of "garbage in, garbage out".

## Core discipline (before any calculation)
**Work out how much you can lose before thinking about how much you might make.** The position
conclusion is **not built on the base case** — it's built on the **downside floor**: recompute
intrinsic value under worst-case assumptions, compare against the current price to get the margin of
safety, and only if the floor still leaves enough buffer can you talk about whether to buy and how
much. This matches Leo's hard rule — position size is derived from the worst case, not from the size
of the opportunity.

## When to use
- You need an absolute valuation anchor (comps only tell you relative cheapness; DCF tells you what
  it's worth).
- You want a quick read on whether the margin of safety is sufficient.
- You want to convert "how much should I buy" from a guess into something derived from the worst case.

## The eight steps (leave a trace at each)

1. **Define target and vantage**: ticker / name plus a buy-side vantage. Record current price, shares
   outstanding, market cap and net debt (net debt = interest-bearing debt − cash).
2. **Take the FCF base**: preferably operating cash flow − capex (from `westock-data` or the filings).
   If FCF isn't disclosed, approximate with net income + D&A − capex and label it "approximate".
3. **Set the two stages**: explicit period N = 5–10 years, with staged or year-by-year growth rates
   (justified by history, industry, consensus). Terminal value uses Gordon (g below long-run GDP /
   inflation) **or** an exit EV/EBITDA multiple — pick one and say why (see
   `references/dcf_methodology.md`).
4. **Set WACC**: discount rate = risk-free + risk premium + beta / size premium. WACC is not a tuning
   knob; assumptions must be defensible (see the defensible ranges and red lines in
   `references/assumptions_bounds.md`).
5. **Compute present value**: the script discounts explicit-period FCF plus discounted terminal value
   to enterprise value; subtract net debt for equity value, divide by shares for intrinsic value per
   share (base case).
6. **Sensitivity**: a WACC × growth (or terminal multiple) matrix giving a range of intrinsic value per
   share, not a point.
7. **Downside derivation (mandatory)**: compress assumptions to worst case (growth cut 30–50%, WACC
   raised 100–150bp, margin compression) and recompute the **downside floor** per share. Compare
   against price for the margin of safety.
8. **Conclude plus position ceiling**: based on the floor, give a **maximum position** (rules in the
   script and `references/assumptions_bounds.md`): floor above 1.5× price → consider building a
   position; 1.0–1.5× → small position only; below 1.0× → don't touch. Name the variables that would
   trigger a re-run.

## Data sources (in priority order; never fabricate)
- `westock-data` first: market cap, net debt, FCF, consensus estimates.
- Fallbacks: `akshare-stock` / `neodata-financial-search` for A-share detail.
- Last resort: `WebSearch` / `WebFetch` — annual reports, IR, quote pages.
- Mark any missing field `N/A` with source and reason. Never fill placeholder numbers.

## Output format (one page of Markdown; structure in `examples/sample-dcf.md`)
- Assumptions table (FCF base, N, growth, WACC, terminal method);
- Discounting table (explicit period + terminal value);
- Sensitivity matrix;
- **Downside floor** block (worst-case assumptions + result + margin of safety);
- Position ceiling conclusion (from the worst case, not the opportunity size);
- Append the raw `scripts/dcf_calc.py` output so it's reproducible.

## Checks and red lines (reliability floor)
- WACC ≤ terminal growth g → the script throws an error (Gordon diverges); do not compute anyway.
- Base-case per share deviating from the comps-implied value by more than 20% → you may not state
  both "buy" and "cheap"; resolve the conflict first.
- The downside floor must be below the base case (worst case cannot exceed the optimistic case) —
  otherwise the assumptions contradict each other.
- Stamp every assumption with data date and source; WACC or growth outside the defensible band in
  `references/assumptions_bounds.md` must be explicitly argued.

## Boundaries and disclaimer
- A DCF is extremely sensitive to assumptions — garbage in, garbage out. Always cross-check with
  `valuation-comps`.
- The downside floor is a discipline tool, not a precise bottom. It answers "can I live with the worst
  case", not "how high will it go".
- Stamp data date and source. Investment decisions belong to a human; this skill produces a
  reproducible analysis skeleton.

## Layout
```
dcf-quick/
  SKILL.md                  # this file (English)
  SKILL_CN.md               # 简体中文版
  README.md
  references/
    dcf_methodology.md      # two-stage model, terminal method choice, discounting detail
    assumptions_bounds.md   # defensible ranges and red lines for WACC / growth / margin
  scripts/
    dcf_calc.py             # calculation core (base / sensitivity / downside floor / position)
    dcf_calc_test.py        # unit tests
  examples/
    sample-dcf.md           # anonymised sample
```
