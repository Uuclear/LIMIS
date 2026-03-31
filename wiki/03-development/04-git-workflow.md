# Git 分支与协作流程

建议使用 **功能分支** + Merge Request / Pull Request：

1. 从 `main`/`develop` 切出 `feature/*` 或 `fix/*`
2. 小步提交，信息写清 **动机与影响范围**
3. CI 通过后合并；数据库迁移需 **向前兼容** 或可回滚说明

与 [发版](../04-deployment/01-deployment-overview.md) 协同。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
