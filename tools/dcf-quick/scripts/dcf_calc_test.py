#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dcf_calc 单测：保证折现、敏感性、下行地板、仓位逻辑可靠。"""
import dcf_calc as D


BASE = {
    "shares": 800, "net_debt": 1200, "price": 18.0,
    "base_fcf": 300, "years": 5,
    "growth": [0.15, 0.12, 0.10, 0.08, 0.06],
    "wacc": 0.09,
    "terminal": {"method": "gordon", "g": 0.025},
    "downside": {"growth_haircut": 0.4, "wacc_uplift_bp": 120, "margin_compression": 0.0},
}


def run():
    # 1) 基准每股（手算参考 ~5.88，容忍 5.5–6.5）
    base = D.compute(BASE, "base")
    assert 5.5 < base["per_share"] < 6.5, f"基准每股应≈5.88，实得 {base['per_share']:.3f}"

    # 2) WACC 越高价值越低（单调性）
    lo = D.per_share_at(BASE, wacc_adj=-0.01)
    hi = D.per_share_at(BASE, wacc_adj=+0.01)
    assert lo > hi, "WACC 升高应使每股价值下降"

    # 3) 终值 g 越高价值越高（Gordon）
    g_lo = D.per_share_at(BASE, term_adj=-0.01)
    g_hi = D.per_share_at(BASE, term_adj=+0.01)
    assert g_hi > g_lo, "终值 g 升高应使每股价值上升"

    # 4) 下行地板必须 < 基准值
    down = D.compute(BASE, "downside")
    assert down["per_share"] < base["per_share"], "下行地板必须低于基准值"

    # 5) WACC<=g 必须报错（红线）
    bad = dict(BASE); bad["terminal"] = {"method": "gordon", "g": 0.10}  # g>wacc
    try:
        D.compute(bad, "base")
        raise AssertionError("WACC<=g 未报错")
    except ValueError:
        pass

    # 6) 仓位档位逻辑
    assert D.position_tier(30.0, 18.0)[0] == "可建仓", "地板/市价=1.67 应可建仓"
    assert D.position_tier(20.0, 18.0)[0] == "小仓", "1.11× 应小仓"
    assert D.position_tier(10.0, 18.0)[0] == "不碰", "0.56× 应不碰"

    # 7) 退出倍数法可用
    em = dict(BASE); em["terminal"] = {"method": "exit_multiple", "multiple": 14.0, "terminal_ebitda": 900}
    r = D.compute(em, "base")
    assert r["per_share"] > 0, "退出倍数法应产出正价值"

    print("✅ dcf_calc 单测全部通过")
    return True


if __name__ == "__main__":
    sys_exit = __import__("sys").exit
    sys_exit(0 if run() else 1)
