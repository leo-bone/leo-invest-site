# dcf-quick

> [English](./README.md) · **简体中文** · [站点](https://leo.uichain.org/)

> 给一个标的，单页产出**两阶段 DCF 估值区间 + 下行地板**，并把"最大仓位"由最坏情况倒推，而非由机会大小正推。
> 投资纪律的量化外骨骼——绝对估值锚。

设计哲学：代码只是表达媒介，**能复用、能复现、能校验**才值得做（致敬 Zara Zhang 的 `frontend-slides`）。

## 为什么可靠
- **算术交给脚本**：`scripts/dcf_calc.py` 做折现、敏感性矩阵、下行地板、仓位倒推，agent 不心算。
- **纪律内建**：下行地板 < 基准值、WACC>g 等红线由脚本强制校验，假设矛盾直接报错。
- **可辩护边界**：`references/assumptions_bounds.md` 给出 WACC/增长率的可辩护范围，超出必须论证。
- **交叉验证**：与 `valuation-comps` 偏离 >20% 时禁止直接下结论。

## 快速开始
```bash
# 跑内置自检
python3 scripts/dcf_calc_test.py

# 用输入 JSON 计算（结构见 examples/input.json）
python3 scripts/dcf_calc.py --input examples/input.json
```

输入 JSON 最小结构：
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

## 八步流程（详见 SKILL.md）
1. 定标的与视角 → 2. 取 FCF 基数 → 3. 设两阶段 → 4. 定 WACC → 5. 算现值 → 6. 敏感性 → 7. 下行倒推 → 8. 仓位上限。

## 仓位倒推规则（核心纪律）
| 下行地板 / 市价 | 档位 | 最大仓位 |
|---|---|---|
| ≥ 1.5× | 可建仓 | 可正常建仓（按组合上限） |
| 1.0× – 1.5× | 小仓 | ≤ 组合 5–10% |
| < 1.0× | 不碰 | 0% |

先确认环境允许进攻（见 `macro-dashboard`），再用本 skill 定买什么、买多少；再用 `valuation-comps` 校验贵贱。

## 许可
MIT。分析结论仅供参考，投资决策由人负责。
