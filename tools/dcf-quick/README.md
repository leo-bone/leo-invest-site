# dcf-quick

单页速算 DCF，并把"最大仓位"由最坏情况倒推，而非由机会大小正推。

## 它解决什么
- 绝对估值锚（相对估值只给贵贱，DCF 给"值多少钱"）；
- 快速判断安全边际是否充足；
- 把"该买多少"从拍脑袋改成"由下行地板倒推"。

## 用法
任何 coding agent 加载 `SKILL.md` 即可跑流程。给一个标的（代码或名称），按八步产出单页报告：
假设表 → 折现计算表 → 敏感性矩阵 → **下行地板** → 仓位上限结论。

## 数据来源
`westock-data`（首选）→ `akshare-stock` / `neodata-financial-search`（补 A 股）→ `WebSearch` / `WebFetch`（兜底）。严禁编造数字。

## 与同仓库其他 skill 的关系
- `valuation-comps`：相对锚，DCF 的交叉验证。
- `macro-dashboard`：自上而下开关——本 skill 解决"买什么、买多少"，macro-dashboard 解决"现在该不该满仓买"。

## 免责
DCF 对假设极敏感；下行地板是纪律工具不是精确底部。决策由人负责。
