# 项目状态摘要（与仓库 `PROJECT_STATUS.md` 对齐）

> **权威来源**：主仓库根目录 **`PROJECT_STATUS.md`**（随迭代更新）。本页仅作 Wiki 侧 **速览与跳转**，重大结论以主仓库文档为准。

---

## 最近一次同步说明（2026-04）

- **统计**：Dashboard 已集成 ECharts（检测量、合格率、强度曲线、项目/方法任务数等）；公开统计接口见主仓库 `backend/apps/statistics/`。
- **报告**：PDF（WeasyPrint）、报告详情预览；**防伪**：公开接口 `GET /api/v1/reports/public/verify/<id>/`，前端免登录页 `/verify/report/:id`；环境变量 **`REPORT_VERIFICATION_URL`** 需与前端部署域名一致。
- **样品**：列表支持批量打印二维码标签（`print-js`）。
- **权限**：用户权限短时缓存 `USER_PERMISSIONS_CACHE_SECONDS`；侧栏按路由 `meta.permission` 过滤。
- **工具链**：前端 `npm run typecheck`、`npm run lint`（ESLint `--quiet`）。
- **Wiki**：`wiki/` 经 **GitHub Actions**（仅 **wiki-sync**）同步至 GitHub Wiki；**Docker/前后端构建类 Actions 已移除**（本机跑通为主）。
- **部署文档**：`wiki/04-deployment/` 已补充 **HTTPS / `REPORT_VERIFICATION_URL`** 与 **PostgreSQL 备份恢复** 要点（与 `PROJECT_STATUS.md` §6.3.1 对应）。

---

## 仍待产品化（节选）

- 报告 **Word** 版式导出、复杂 **审批链** 与电子签章。
- 委托/样品 **Excel 模板**批量导入等。
- 通知中心 **后端** 与顶栏示例数据替换。

详细勾选清单请直接阅读主仓库 **`PROJECT_STATUS.md`** §6。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.1 | Wiki | 部署 wiki 与 §6.3.1 文档对齐说明 |
| 2026-04-01 | 1.0 | Wiki | 初版：与 PROJECT_STATUS 对齐的 Wiki 摘要 |

返回：[Wiki 首页](../README.md)
