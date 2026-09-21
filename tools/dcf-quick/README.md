# dcf-quick

> **English** · [简体中文](README_CN.md) · [Site](https://leo.uichain.org/)

[![CI](https://github.com/leo-bone/dcf-quick/actions/workflows/test.yml/badge.svg)](https://github.com/leo-bone/dcf-quick/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen.svg)](scripts/)
[![Agent Skill](https://img.shields.io/badge/agent--skill-Claude%20%C2%B7%20Codex%20%C2%B7%20WorkBuddy-blueviolet.svg)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**A one-page DCF that tells you how much to buy — not just what it's worth.**

Most DCFs answer "what is this worth?" and stop there. That number is then used to justify a
position size chosen by enthusiasm. This skill inverts the order: it computes a **downside
floor** first, and derives the **maximum position from the worst case** rather than from how
large the upside looks.

```
### 下行地板（worst-case）
- 假设：增长下修 40%、WACC +120bp、利润率/倍数压缩 0%
- **下行地板每股：25.33**
- 当前市价：18.00 ｜ 安全边际（地板/市价）：1.41×

### 仓位倒推（由最坏情况，非机会大小）
- **档位：小仓** ｜ 下行地板/市价=1.41×，仅小仓（≤组合 5–10%）
```

## Quick start

```bash
python3 scripts/dcf_calc_test.py                        # verify the math (CI runs this too)
python3 scripts/dcf_calc.py --input examples/input.json # run the sample
```

Minimal input:

```json
{
  "shares": 800, "net_debt": 1200, "price": 18.0,
  "base_fcf": 300, "years": 5,
  "growth": [0.15, 0.12, 0.10, 0.08, 0.06],
  "wacc": 0.09,
  "terminal": {"method": "gordon", "g": 0.025},
  "downside": {"growth_haircut": 0.4, "wacc_uplift_bp": 120, "margin_compression": 0.0}
}
```

Point your agent at [`SKILL.md`](SKILL.md). Stdlib only, no pip install.

## What comes out

1. **Base-case intrinsic value per share** — 2-stage FCF, explicit period + terminal value
2. **Sensitivity matrix** — WACC × terminal growth, so you see how much of your answer is assumption
3. **Downside floor** — growth haircut, WACC uplift, margin compression applied together
4. **Position cap** — a tier, not a suggestion

### Position sizing rule

| Downside floor / market price | Tier | Max position |
|---|---|---|
| ≥ 1.5× | Build | up to your normal portfolio limit |
| 1.0× – 1.5× | Small | ≤ 5–10% of portfolio |
| < 1.0× | Don't touch | 0% |

The floor is not a price target. It is the number that decides size.

## Guardrails built into the script

- **`WACC ≤ g` raises an error.** A Gordon terminal value with growth at or above the discount
  rate is not a valuation, it's a typo with a decimal point.
- **The downside floor must sit below the base case.** If your stress case is higher than your
  base case, your assumptions contradict each other.
- **Assumption ranges must be defensible.** [`references/assumptions_bounds.md`](references/assumptions_bounds.md)
  gives the ranges for WACC and growth; stepping outside them requires written justification.
- **A >20% gap vs. comps blocks the conclusion.**
- Methodology, including why terminal value dominates the answer and what to do about it:
  [`references/dcf_methodology.md`](references/dcf_methodology.md)

## The 8 steps

Frame the target → get a clean FCF base → set two stages → pin the WACC → discount → run the
sensitivity grid → stress to the floor → size the position.

## Part of a three-skill loop

| Skill | Question it answers |
|---|---|
| [**macro-dashboard**](https://github.com/leo-bone/macro-dashboard) | Should I be deploying capital at all right now? |
| [**valuation-comps**](https://github.com/leo-bone/valuation-comps) | Is this cheap or expensive relative to its peers? |
| **dcf-quick** (here) | What is it worth, what is my downside, how big a position? |

Check the macro switch before you size anything. A great floor in a risk-off regime is still
a bad trade.

## License

MIT. A model is not a forecast. The decision stays yours.
