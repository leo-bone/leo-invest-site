# Leo 的投资站点

个人站点：投资分析文章 + 可复用分析工具（agent skill）。

## 结构
- `index.html` / `assets/`：编辑型静态站点（关于 / 文章流 / 工具展示 / 联系）
- `posts/`：投资分析文章（Comps 框架、2026 宏观四变量、判断复盘）
- `tools/`：三个开源 agent skill
  - `valuation-comps`：可比公司估值（八步）
  - `dcf-quick`：单页 DCF + 下行倒推仓位
  - `macro-dashboard`：宏观四变量周更攻守面板

## 本地预览
```bash
python3 -m http.server 8123
# 打开 http://127.0.0.1:8123/index.html
```

## 部署
GitHub Pages：仓库根即站点根，Settings → Pages → Source: main / root。
或用任意静态托管（Vercel / Netlify / Cloudflare Pages）。零成本。
