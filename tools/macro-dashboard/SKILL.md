---
name: macro-dashboard
title: Macro Dashboard — Weekly Four-Variable Regime Panel
summary: Refresh four driving variables weekly (rates / credit / earnings expectations / liquidity) and output an attack-or-defend switch rather than a price forecast. Turns the discipline of sizing from the worst case into a panel you can update every week.
read_when:
  - user wants a weekly or periodic review of how the macro environment affects risk assets
  - user asks "should I be attacking or defending right now"
  - user mentions "macro" "risk-on risk-off" "position switch" "four variables" "risk asset environment"
---

> **English** · [简体中文](SKILL_CN.md)

# Macro Dashboard

A skill that makes macro monitoring **structured, weekly-refreshable and reproducible**. It does not
forecast price levels — it tracks the four variables that drive the pricing of risk assets and outputs
an **attack/defend switch**. This is the top-down switch layer above `valuation-comps` and
`dcf-quick`: those two answer "what to buy and what it's worth", this one answers "should you be
buying at full size right now".

**Run `scripts/score_snapshot.py` for the regime call**: the agent fetches the latest values and the
status of each variable, while the script computes the aggregate and applies the hard rules — so nobody
"optimistically adjusts" the stance.

## The four variables (the transmission chain)
1. **Rates**: the direction of *real* rates (nominal rate − inflation expectations). Rising compresses
   long-duration assets; falling repairs risk appetite. Watch real rates, not what the Fed says.
2. **Credit**: whether the system suddenly runs short of money. High-yield spreads, commercial paper
   spreads, offshore dollar liquidity — any of them widening quickly is the pre-symptom of a margin call.
3. **Earnings expectations**: whether the story can be cashed in. The breadth of revisions (number
   upgraded versus downgraded) leads EPS growth rates.
4. **Liquidity**: whether the pool is filling or draining. Central bank balance sheets, reverse repos,
   broad money growth.

## Five steps (same slot every week)
1. **Fetch at a fixed slot**: pull the latest value of each variable at the same time each week
   (e.g. Sunday). Sources below.
2. **Three-state call**: rate each variable friendly / neutral / alert, with the signal and the number
   (the script can classify automatically against thresholds — see `references/indicators.md`).
3. **Aggregate**: green-light count maps to the attack stance. The script applies the rules (see
   `references/regime_rules.md`).
4. **Output the panel**: a table plus a one-line conclusion (attack or defend, with the reason).
   **No price forecasts.**
5. **Keep a trace**: append to the `macro-dashboard.md` snapshot so you can look back at where signals
   turned.

## Data sources (in priority order; never fabricate)
- `westock-data` / `macro-monitor` skill: rates, spreads, liquidity indicators.
- `WebSearch` / `WebFetch`: Federal Reserve, central banks, consensus sources.
- Fallback: quote pages / financial terminals. Mark missing items `N/A` with a note.

## Output format
`macro-dashboard.md`: a four-variable table (variable / latest value / status light / signal) plus the
attack-or-defend conclusion plus the triggers to watch next week. Structure in
`examples/sample-dashboard.md`. Append the `scripts/score_snapshot.py` output as a trace.

## Checks and red lines (reliability floor)
- **Credit or liquidity at alert = forced defence**, overriding the green-light count (a hard rule —
  "I think it can hold" is not permitted).
- When any variable is `N/A`, it doesn't count toward the green lights, but the conclusion must state
  explicitly that "X is unknown, confidence is reduced".
- The stance gives directional guidance only, never price levels; pair it with the `dcf-quick` downside
  floor to get "how much to buy".

## Boundaries and disclaimer
- The four variables are a switch, not a scorecard. Credit and liquidity both alerting means defend,
  without hesitation.
- Consistent with sizing from the worst case: confirm the environment permits attack, then use
  `dcf-quick` to decide what and how much, then `valuation-comps` to check whether it's cheap or dear.
- Conclusions support judgement; decisions belong to a human.

## Layout
```
macro-dashboard/
  SKILL.md                  # this file (English)
  SKILL_CN.md               # 简体中文版
  README.md
  references/
    indicators.md           # concrete indicators, sources and thresholds for the four variables
    regime_rules.md         # attack/defend rules, credit & liquidity hard override
  scripts/
    score_snapshot.py       # regime call (hard rules included)
    score_snapshot_test.py
  examples/
    sample-dashboard.md
```
