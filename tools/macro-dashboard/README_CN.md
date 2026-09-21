# macro-dashboard

> [English](./README.md) · **简体中文** · [站点](https://leo.uichain.org/)

> 每周刷新四个驱动变量（利率 / 信用 / 盈利预期 / 流动性），输出"攻守开关"而非点位预测。
> 把"仓位由最坏情况倒推"的纪律变成可周更的仪表盘——自上而下开关层。

设计哲学：代码只是表达媒介，**能复用、能复现、能校验**才值得做（致敬 Zara Zhang 的 `frontend-slides`）。

## 为什么可靠
- **硬规则内建**：信用或流动性任一警戒 = 强制防守，脚本覆盖绿灯数，避免人为乐观调整档位。
- **阈值可配置**：`references/indicators.md` 给出四变量的具体指标与判定阈值，agent 按阈值分类而非拍脑袋。
- **可周更留痕**：每周 append 快照，回看信号转折。

## 快速开始
```bash
# 跑内置自检
python3 scripts/score_snapshot_test.py

# 用输入 JSON 判档位（结构见 examples/input.json）
python3 scripts/score_snapshot.py --input examples/input.json
```

输入 JSON 结构（状态可由 agent 直接给，或给数值+阈值由脚本分类）：
```json
{
  "date": "2026-09-20",
  "variables": {
    "interest": {"value": 1.8, "direction": "lower_better",
                 "thresholds": {"friendly": 1.5, "alert": 2.5},
                 "note": "实际利率 1.8%，走平"},
    "credit":   {"state": "friendly", "note": "HY 利差 320bp，收窄"},
    "earnings": {"state": "neutral", "note": "盈利修正广度 50%"},
    "liquidity":{"state": "alert", "note": "央行缩表"}
  }
}
```

## 攻守档位规则
| 绿灯数 | 档位 |
|---|---|
| 4 | 满格进攻 |
| 3 | 进攻 |
| 2 | 中性 |
| 1 | 防御 |
| 0 | 全面防御 |

**硬规则**：信用或流动性任一警戒 → 强制防守（覆盖绿灯数）。

## 与同系列 skill 的关系
- `macro-dashboard`：现在该不该满仓买（开关）。
- `dcf-quick`：买什么、下行地板与仓位倒推（定价 + 纪律）。
- `valuation-comps`：相对贵贱校验（相对锚）。
- 闭环：宏观开关 → 选股（comps）→ 定价与仓位（dcf）。

## 许可
MIT。结论仅供参考，投资决策由人负责。
