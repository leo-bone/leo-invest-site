# macro-dashboard

> **English** · [简体中文](README_CN.md) · [Site](https://leo.uichain.org/)

[![CI](https://github.com/leo-bone/macro-dashboard/actions/workflows/test.yml/badge.svg)](https://github.com/leo-bone/macro-dashboard/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen.svg)](scripts/)
[![Agent Skill](https://img.shields.io/badge/agent--skill-Claude%20%C2%B7%20Codex%20%C2%B7%20WorkBuddy-blueviolet.svg)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**A weekly regime switch, not a price forecast.**

Four variables — rates, credit, earnings expectations, liquidity — refreshed weekly and turned
into one word: attack, neutral, or defend. No target prices, no "the market will…". Just the
question that actually governs how much risk you should be carrying.

```
**日期**：2026-09-20 ｜ **绿灯数**：1/4

| 变量 | 状态 | 信号 |
|---|---|---|
| 利率 | 🟡 neutral | 实际利率 1.8%，走平 |
| 信用 | 🟢 friendly | HY 利差 320bp，收窄 |
| 盈利预期 | 🟡 neutral | 盈利修正广度 50% |
| 流动性 | 🔴 alert | 央行缩表，基础货币同比转负 |

### 攻守结论：**强制防守（信用/流动性报警）**
```

Note what happened here: only one light is green, but the verdict is driven by a **hard rule**,
not a vote.

## The hard rule

> **If credit OR liquidity is on alert → forced defense, regardless of green-light count.**

Three friendly variables cannot outvote broken credit. Credit and liquidity are the two that
break first and break fastest; the script encodes that rather than leaving it to judgement in
the moment. See [`references/regime_rules.md`](references/regime_rules.md).

| Green lights | Regime |
|---|---|
| 4 | Full attack |
| 3 | Attack |
| 2 | Neutral |
| 1 | Defense |
| 0 | Full defense |

## Quick start

```bash
python3 scripts/score_snapshot_test.py                       # verify the rules (CI runs this too)
python3 scripts/score_snapshot.py --input examples/input.json # run the sample
```

You can hand it either a state or a number plus thresholds — the script classifies:

```json
{
  "date": "2026-09-20",
  "variables": {
    "interest": {"value": 1.8, "direction": "lower_better",
                 "thresholds": {"friendly": 1.5, "alert": 2.5},
                 "note": "实际利率 1.8%，走平"},
    "credit":    {"state": "friendly", "note": "HY 利差 320bp，收窄"},
    "earnings":  {"state": "neutral",  "note": "盈利修正广度 50%"},
    "liquidity": {"state": "alert",    "note": "央行缩表"}
  }
}
```

Exact indicator definitions and threshold values live in
[`references/indicators.md`](references/indicators.md), so the agent classifies against a written
standard instead of improvising one each week.

## Why weekly

One-off macro reads decay immediately. Append a dated snapshot every week and you get something
more valuable than any single call: **a record of when the signal actually turned**, which you
can compare against what you believed at the time.

## Part of a three-skill loop

| Skill | Question it answers |
|---|---|
| **macro-dashboard** (here) | Should I be deploying capital at all right now? |
| [**valuation-comps**](https://github.com/leo-bone/valuation-comps) | Is this cheap or expensive relative to its peers? |
| [**dcf-quick**](https://github.com/leo-bone/dcf-quick) | What is it worth, what is my downside, how big a position? |

Switch first, screen second, price third. This skill sets the ceiling on risk; the other two
decide what to do inside it.

## License

MIT. A regime call is a starting position for thinking, not a trading signal.
