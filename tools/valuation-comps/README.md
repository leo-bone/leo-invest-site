# valuation-comps

给一个标的（代码或名称），自动跑完**可比公司分析（trading comps）**的八步流程，输出对齐口径的 Comps 表与隐含估值区间。

> 设计哲学：代码只是表达媒介，**能复用、能复现**才值得做。（路线参考 Zara Zhang 的 `frontend-slides`）

## 它能做什么
- 选 peer（业务同质 + 规模可比 + 市场相同，不按行业标签硬凑）
- 取 EV/Rev、EV/EBITDA、P/E 等倍数，统一 NTM / FY+1 口径
- 报告中位数 + 25/75 分位，给估值区间而非单点
- 与 DCF / 交易可比交叉验证，输出"贵 / 合理 / 便宜"结论与重估触发条件

## 用法
任何 coding agent 加载本目录的 `SKILL.md` 即可。触发词：`comps` / `可比公司` / `相对估值` / `peer multiples`。

数据来源优先级：`westock-data` → `akshare-stock` / `neodata-financial-search` → `WebSearch` / `WebFetch`。
**严禁编造数字**，缺失字段标 `N/A`。

## 目录
```
valuation-comps/
  SKILL.md            # 流程与规范（agent 读取）
  examples/
    sample-comps.md   # 脱敏示例报告
  README.md           # 本文件
```

## 许可
MIT（示例数据除外，示例仅供演示）。
