#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""score_snapshot 单测：保证分类、绿灯计数、硬规则可靠。"""
import score_snapshot as S


def run():
    # 1) 数值分类 lower_better
    assert S.classify({"value": 1.2, "direction": "lower_better",
                       "thresholds": {"friendly": 1.5, "alert": 2.5}}) == "friendly"
    assert S.classify({"value": 2.0, "direction": "lower_better",
                       "thresholds": {"friendly": 1.5, "alert": 2.5}}) == "neutral"
    assert S.classify({"value": 3.0, "direction": "lower_better",
                       "thresholds": {"friendly": 1.5, "alert": 2.5}}) == "alert"

    # 2) 数值分类 higher_better
    assert S.classify({"value": 60, "direction": "higher_better",
                       "thresholds": {"friendly": 55, "alert": 45}}) == "friendly"
    assert S.classify({"value": 40, "direction": "higher_better",
                       "thresholds": {"friendly": 55, "alert": 45}}) == "alert"

    # 3) 直接给 state
    assert S.classify({"state": "neutral"}) == "neutral"

    # 4) N/A 不计入
    assert S.classify({"state": "N/A"}) is None
    assert S.classify({"na": True}) is None

    # 5) 4 绿 → 满格进攻
    d = {"date": "t", "variables": {k: {"state": "friendly"} for k in S.REQUIRED}}
    _, greens, regime, fd, na = S.score(d)
    assert greens == 4 and regime == "满格进攻" and not fd

    # 6) 信用警戒 → 强制防守（覆盖绿灯数）
    d2 = {"date": "t", "variables": {
        "interest": {"state": "friendly"}, "credit": {"state": "alert"},
        "earnings": {"state": "friendly"}, "liquidity": {"state": "friendly"}}}
    _, greens, regime, fd, na = S.score(d2)
    assert greens == 3 and fd and regime.startswith("强制防守")

    # 7) 流动性警戒 → 强制防守
    d3 = dict(d2); d3["variables"]["liquidity"] = {"state": "alert"}; d3["variables"]["credit"] = {"state": "friendly"}
    _, greens, regime, fd, na = S.score(d3)
    assert fd and regime.startswith("强制防守")

    # 8) N/A 变量 → na_vars 记录，不计入绿灯
    d4 = {"date": "t", "variables": {
        "interest": {"state": "friendly"}, "credit": {"na": True},
        "earnings": {"state": "neutral"}, "liquidity": {"state": "alert"}}}
    _, greens, regime, fd, na = S.score(d4)
    assert "信用" in na and greens == 1

    print("✅ score_snapshot 单测全部通过")
    return True


if __name__ == "__main__":
    sys_exit = __import__("sys").exit
    sys_exit(0 if run() else 1)
