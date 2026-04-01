# 测试策略与执行

- **后端**：`pytest` / Django `TestCase`，覆盖权限、序列化与关键服务。
- **前端**：组件与 E2E（若有 Playwright/Cypress）按团队约定。
- **发版前**：冒烟测试登录、主流程单据、报告导出。
- **CI**：仓库已移除 Docker/前后端 **GitHub Actions 构建流水线**；日常以本机 `manage.py check` / `npm run typecheck` / `npm run lint` 等为准；**Wiki 同步** 仍由 `.github/workflows/wiki-sync.yml` 负责（见 [GitHub Wiki 同步](07-github-wiki-sync.md)）。

详见 [贡献指南](06-contributing-guide.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |
| 2026-04-01 | 1.1 | Wiki | 说明已移除构建类 Actions，保留 Wiki 同步 |

返回：[Wiki 首页](../README.md)
