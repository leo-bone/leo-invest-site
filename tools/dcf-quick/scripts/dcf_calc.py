#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dcf-quick 计算内核。

职责：输入假设，输出
  1) 基准情形：两阶段 DCF 每股内在价值（折现显式期 + 折现终值 − 净负债）；
  2) 敏感性矩阵（WACC × 终值）；
  3) 下行地板（worst-case 假设下的最低每股价值）；
  4) 由下行地板倒推的仓位上限档位。

设计原则：
  - 不联网、不编造；agent 只负责取数定假设，算术交给本脚本。
  - 红线由脚本强制：WACC ≤ g 直接报错；下行地板必须 < 基准值，否则假设矛盾报错。
  - 全部可复现：输入 JSON 固定则输出固定。

用法：
  python3 dcf_calc.py --input input.json
  python3 dcf_calc.py --selftest
"""
import json
import sys
import argparse


def growth_series(base_growth, years):
    if isinstance(base_growth, (int, float)):
        return [float(base_growth)] * years
    g = [float(x) for x in base_growth]
    if len(g) < years:
        g = g + [g[-1]] * (years - len(g))
    return g[:years]


def compute(data, scenario="base"):
    shares = float(data["shares"])
    net_debt = float(data.get("net_debt", 0) or 0)
    base_fcf = float(data["base_fcf"])
    years = int(data["years"])
    wacc = float(data["wacc"])
    term = data["terminal"]
    growth = data.get("growth", 0.10)

    margin_compression = 0.0
    if scenario == "downside":
        d = data.get("downside", {})
        gh = float(d.get("growth_haircut", 0.4))
        wu = float(d.get("wacc_uplift_bp", 120)) / 10000.0
        margin_compression = float(d.get("margin_compression", 0.0))
        growth = [g * (1 - gh) for g in growth_series(growth, years)]
        wacc = wacc + wu
    else:
        growth = growth_series(growth, years)

    # 显式期 FCF 与现值
    fcf = []
    f = base_fcf
    for i in range(years):
        if i > 0:
            f = f * (1 + growth[i])
        fcf.append(f)
    pv_explicit = sum(fcf[i] / (1 + wacc) ** (i + 1) for i in range(years))

    # 终值
    last = fcf[-1]
    if term["method"] == "gordon":
        g = float(term["g"])
        if wacc <= g:
            raise ValueError(f"WACC({wacc:.4f}) <= g({g:.4f})，Gordon 公式发散，请修正假设")
        tv = last * (1 + g) / (wacc - g)
    elif term["method"] == "exit_multiple":
        mult = float(term["multiple"]) * (1 - margin_compression)
        ebitda_base = float(term.get("terminal_ebitda", last))
        tv = ebitda_base * (1 + growth[-1]) * mult
    else:
        raise ValueError("terminal.method 必须是 gordon 或 exit_multiple")

    pv_tv = tv / (1 + wacc) ** years
    ev = pv_explicit + pv_tv
    equity = ev - net_debt
    per_share = equity / shares
    return {
        "fcf": fcf, "pv_explicit": pv_explicit, "tv": tv, "pv_tv": pv_tv,
        "ev": ev, "equity": equity, "per_share": per_share, "wacc": wacc,
        "growth": growth, "margin_compression": margin_compression,
    }


def per_share_at(data, wacc_adj=0.0, term_adj=0.0):
    d = json.loads(json.dumps(data))
    d["wacc"] = float(data["wacc"]) + wacc_adj
    if d["terminal"]["method"] == "gordon":
        d["terminal"]["g"] = float(data["terminal"]["g"]) + term_adj
    else:
        d["terminal"]["multiple"] = float(data["terminal"]["multiple"]) + term_adj
    return compute(d, "base")["per_share"]


def position_tier(floor_ps, price):
    if not price or price <= 0:
        return ("N/A", "未提供市价，无法倒推仓位", None)
    r = floor_ps / price
    if r >= 1.5:
        return ("可建仓", f"下行地板/市价={r:.2f}×，安全边际充足，可正常建仓（受组合上限约束）", r)
    if r >= 1.0:
        return ("小仓", f"下行地板/市价={r:.2f}×，仅小仓（≤组合 5–10%）", r)
    return ("不碰", f"下行地板/市价={r:.2f}×，安全边际不足", r)


def render_md(data):
    base = compute(data, "base")
    down = compute(data, "downside")
    if down["per_share"] >= base["per_share"]:
        raise ValueError("下行地板(%.3f) ≥ 基准值(%.3f)，worst-case 假设矛盾，请检查"
                         % (down["per_share"], base["per_share"]))
    price = float(data.get("price", 0) or 0)
    tier, note, r = position_tier(down["per_share"], price)

    L = []
    L.append(f"### 基准情形（每股内在价值）")
    L.append(f"- 显式期 PV(FCF)：{base['pv_explicit']:.1f}")
    L.append(f"- 终值 TV（现值）：{base['tv']:.1f}（{base['pv_tv']:.1f}）")
    L.append(f"- 企业价值 EV：{base['ev']:.1f} ｜ 减净负债：{float(data.get('net_debt',0) or 0):.1f}")
    L.append(f"- **每股内在价值：{base['per_share']:.2f}**")
    L.append("")
    L.append("### 敏感性矩阵（每股）")
    L.append("| WACC \\ 终值 | -adj | 基准 | +adj |")
    L.append("|---|---|---|---|")
    if data["terminal"]["method"] == "gordon":
        tadj = 0.01
        tlabel = "g±0.01"
    else:
        tadj = 2.0
        tlabel = "倍数±2x"
    for wa in (-0.01, 0.0, 0.01):
        row = [f"WACC{wa>=0 and '+' or ''}{wa:.02f}"]
        for ta in (-tadj, 0.0, tadj):
            row.append(f"{per_share_at(data, wa, ta):.2f}")
        L.append("| " + " | ".join(row) + " |")
    L.append(f"（终值调整维度：{tlabel}）")
    L.append("")
    L.append("### 下行地板（worst-case）")
    L.append(f"- 假设：增长下修 {int(float(data.get('downside',{}).get('growth_haircut',0.4))*100)}%、"
             f"WACC +{data.get('downside',{}).get('wacc_uplift_bp',120)}bp、"
             f"利润率/倍数压缩 {int(float(data.get('downside',{}).get('margin_compression',0.0))*100)}%")
    L.append(f"- **下行地板每股：{down['per_share']:.2f}**")
    if price > 0:
        L.append(f"- 当前市价：{price:.2f} ｜ 安全边际（地板/市价）：{down['per_share']/price:.2f}×")
    L.append("")
    L.append("### 仓位倒推（由最坏情况，非机会大小）")
    L.append(f"- **档位：{tier}** ｜ {note}")
    L.append("")
    L.append("> 计算内核：scripts/dcf_calc.py。与 valuation-comps 偏离 >20% 须复盘；投资决策由人负责。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        import dcf_calc_test
        sys.exit(0 if dcf_calc_test.run() else 1)
    if not args.input:
        print("⛔ 需提供 --input <json> 或 --selftest")
        sys.exit(1)
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(render_md(data))


if __name__ == "__main__":
    main()
