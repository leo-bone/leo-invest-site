#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macro-dashboard 攻守档位判定内核。

职责：输入四变量（利率/信用/盈利预期/流动性）的状态或数值+阈值，输出
  1) 每变量状态灯与信号；
  2) 绿灯数；
  3) 攻守档位（含硬规则：信用/流动性任一警戒 → 强制防守）。

设计原则：
  - 不联网、不编造；agent 取数，脚本判定档位，避免人为乐观调整。
  - 硬规则覆盖绿灯数，不可被"我觉得还能扛"推翻。
  - 任变量 N/A 不计入绿灯，但结论显式标注置信度下降。

用法：
  python3 score_snapshot.py --input input.json
  python3 score_snapshot.py --selftest
"""
import json
import sys
import argparse


STATE_ORDER = {"friendly": 2, "neutral": 1, "alert": 0}
REGIME = {4: "满格进攻", 3: "进攻", 2: "中性", 1: "防御", 0: "全面防御"}

# 中文展示名（输入 key → 展示）
LABELS = {
    "interest": "利率",
    "credit": "信用",
    "earnings": "盈利预期",
    "liquidity": "流动性",
}
REQUIRED = ["interest", "credit", "earnings", "liquidity"]


def classify(var):
    """返回三态；若已给 state 直接用，否则按数值+阈值分类。N/A → None。"""
    if var.get("na") or var.get("state") == "N/A":
        return None
    if "state" in var and var["state"] in STATE_ORDER:
        return var["state"]
    # 数值分类
    v = var.get("value")
    th = var.get("thresholds")
    direction = var.get("direction", "lower_better")
    if v is None or th is None:
        return None
    v = float(v)
    if direction == "lower_better":
        if v <= float(th["friendly"]):
            return "friendly"
        if v >= float(th["alert"]):
            return "alert"
        return "neutral"
    else:  # higher_better
        if v >= float(th["friendly"]):
            return "friendly"
        if v <= float(th["alert"]):
            return "alert"
        return "neutral"


def score(data):
    results = {}
    na_vars = []
    for key in REQUIRED:
        var = data.get("variables", {}).get(key, {})
        st = classify(var)
        if st is None:
            na_vars.append(LABELS.get(key, key))
        results[key] = {
            "label": LABELS.get(key, key),
            "state": st,
            "note": var.get("note", ""),
            "na": st is None,
        }
    greens = sum(1 for r in results.values() if r["state"] == "friendly")
    credit_alert = results["credit"]["state"] == "alert"
    liq_alert = results["liquidity"]["state"] == "alert"
    forced_def = credit_alert or liq_alert

    if forced_def:
        regime = "强制防守（信用/流动性报警）"
    else:
        regime = REGIME[greens]
    return results, greens, regime, forced_def, na_vars


def render_md(data):
    results, greens, regime, forced_def, na_vars = score(data)
    L = []
    L.append(f"**日期**：{data.get('date','?')} ｜ **绿灯数**：{greens}/4")
    L.append("")
    L.append("| 变量 | 状态 | 信号 |")
    L.append("|---|---|---|")
    icon = {"friendly": "🟢", "neutral": "🟡", "alert": "🔴", None: "⚪"}
    for key in REQUIRED:
        r = results[key]
        st = r["state"]
        L.append(f"| {r['label']} | {icon[st]} {st or 'N/A'} | {r['note']} |")
    L.append("")
    L.append(f"### 攻守结论：**{regime}**")
    if forced_def:
        L.append("- 硬规则触发：信用或流动性警戒 → 强制防守（覆盖绿灯数）。")
    if na_vars:
        L.append(f"- ⚠️ 未知变量：{', '.join(na_vars)}，结论置信度下降。")
    trigger = data.get("next_watch", "下周关注：四变量是否出现转折（尤其信用/流动性）。")
    L.append(f"- {trigger}")
    L.append("")
    L.append("> 计算内核：scripts/score_snapshot.py。只给攻守指引，不给点位；与 dcf-quick 配合定仓位。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        import score_snapshot_test
        sys.exit(0 if score_snapshot_test.run() else 1)
    if not args.input:
        print("⛔ 需提供 --input <json> 或 --selftest")
        sys.exit(1)
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(render_md(data))


if __name__ == "__main__":
    main()
