# 运维 FAQ

本文面向 **运维工程师**、**系统管理员** 与 **值班人员**，覆盖 **部署、配置、日志、备份、性能、安全与应急** 等常见问题，并与 [例行巡检清单](../09-operations-maintenance/01-routine-inspection-checklist.md)、[事件响应](../09-operations-maintenance/04-incident-handling.md) 交叉引用。

**相关主文档**：[部署总览](../04-deployment/01-deployment-overview.md) · [配置与密钥](../04-deployment/03-configuration-and-secrets.md) · [日志与监控](../09-operations-maintenance/02-logs-and-monitoring.md) · [数据库运维](../09-operations-maintenance/03-database-operations.md)  
**既有补充**：[管理员概览与日常清单](../03-admin-guides/01-admin-overview-and-daily-checklist.md)

---

## 目录

1. [可用性与健康检查](#1-可用性与健康检查)
2. [配置、密钥与环境](#2-配置密钥与环境)
3. [日志与排障](#3-日志与排障)
4. [数据库与备份](#4-数据库与备份)
5. [性能与容量](#5-性能与容量)
6. [安全与合规运维](#6-安全与合规运维)
7. [发版与回滚](#7-发版与回滚)
8. [与业务 FAQ 的交界](#8-与业务-faq-的交界)

---

## 1. 可用性与健康检查

### Q1.1 首页能打开，但接口全部 502/504？

优先区分 **静态资源** 与 **API**：

- 静态 OK、API 502：通常是 **上游应用进程未监听**、**反向代理 upstream 配置错误** 或 **网关超时**。参见 [反向代理与 TLS](../04-deployment/04-reverse-proxy-and-tls.md)、[运行时与进程](../04-deployment/02-runtime-and-process.md)。
- 全部不可达：网络、DNS、防火墙或负载均衡健康检查失败。

### Q1.2 健康检查接口应返回什么？

以现场约定为准；常见为 HTTP 200 + 简单 JSON。若健康检查仅验证进程存在而不连数据库，可能出现 **假健康**（进程活着但业务不可用）。建议在 [巡检清单](../09-operations-maintenance/01-routine-inspection-checklist.md) 中区分 **liveness** 与 **readiness**。

### Q1.3 用户大规模被登出，是否事故？

可能是 **统一重新部署**、**密钥轮换** 或 **批量踢出会话**。先确认是否有 **变更单**；若无，检查是否 **误触用户表的 session_version 批量更新** 或 **JWT 签名密钥变更**。参见 [登录权限 FAQ](01-login-permission-and-session-faq.md)。

---

## 2. 配置、密钥与环境

### Q2.1 `SECRET_KEY`、JWT 签名密钥轮换要注意什么？

轮换会导致 **所有已签发 Token 失效**，用户需重新登录。应选择 **业务低峰窗口**，并提前公告。详见 [配置项与密钥管理](../04-deployment/03-configuration-and-secrets.md)。

### Q2.2 数据库连接串、Redis 缓存配置错误会怎样？

- **数据库**：迁移/启动失败，或运行期 **随机 500**（连接池耗尽）。
- **缓存**：若用于登录失败计数等，可能导致 **锁定策略异常** 或 **会话相关键丢失**。

配置分层（dev/staging/prod）建议在 [部署总览](../04-deployment/01-deployment-overview.md) 中维护清单。

### Q2.3 环境变量与 `.env` 文件谁优先？

以项目启动脚本与 Django `settings` 实现为准；**禁止** 将生产密钥提交到 Git。参见 [本地开发](../03-development/01-local-development-setup.md) 与密钥文档。

---

## 3. 日志与排障

### Q3.1 日志在哪里看？

常见位置：

- **应用日志**：stdout（容器）、或 `logs/` 目录（视部署而定）。
- **反向代理**：`access.log` / `error.log`。
- **数据库**：慢查询日志、主从复制延迟。

汇总见 [日志与监控](../09-operations-maintenance/02-logs-and-monitoring.md)。

### Q3.2 如何快速定位 500 错误？

1. 根据 **请求 ID / 时间 / 用户** 在应用日志中搜 traceback。
2. 区分 **代码异常** 与 **依赖不可用**（DB、Redis、外部 HTTP）。
3. 若是 **迁移未执行** 导致列不存在，查 Django migration 状态。

### Q3.3 CORS、CSRF 问题算前端还是运维？

跨域配置可能涉及 **Nginx** 与 **Django CORS 设置** 双方；应 **对照环境** 排查，避免生产放开过度宽松的 `Access-Control-Allow-Origin: *` 与敏感接口并存。参见 [部署与配置](../04-deployment/03-configuration-and-secrets.md)。

---

## 4. 数据库与备份

### Q4.1 备份频率与保留策略谁定？

由 **RPO/RTO** 与合规要求决定。至少保证 **可恢复到发版前一刻** 与 **周期性演练恢复**。步骤见 [备份与恢复](../04-deployment/05-backup-and-recovery.md) 与 [数据库运维](../09-operations-maintenance/03-database-operations.md)。

### Q4.2 磁盘快满了，先删什么？

**勿随意删** 数据库数据目录或 WAL。优先：轮转日志、清理临时导出文件、扩容磁盘。删除前确认 [备份](../04-deployment/05-backup-and-recovery.md) 有效。

### Q4.3 迁移（migration）冲突如何处理？

应在 **预发布环境** 先执行合并与 `--plan` 检查；生产需 **维护窗口** 与 **回滚预案**。研发流程见 [Git 与协作](../03-development/04-git-workflow.md)。

---

## 5. 性能与容量

### Q5.1 接口变慢，先查什么？

- 数据库 **慢查询**、缺失索引；
- **N+1 查询**（DRF 未 `select_related`）；
- **Redis/缓存命中率**；
- **前端大包体** 与 **网关超时**。

### Q5.2 文件上传体积限制在哪里调？

可能在 **Nginx `client_max_body_size`**、**Django `DATA_UPLOAD_MAX_MEMORY_SIZE`**、或 **对象存储 SDK** 层。需 **一致调大**，否则表现为截断或 413。

---

## 6. 安全与合规运维

### Q6.1 如何审计管理员操作？

通过 **系统管理 → 操作日志** 与后端审计表（若有）。详见 [审计与操作日志](../08-security-compliance/02-audit-trail.md) 与 [审计日志运维](../03-admin-guides/06-audit-log-operations.md)。

### Q6.2 漏洞扫描报 Django/依赖 CVE，如何处理？

评估 **可利用性** 与 **修复版本**；在测试环境验证后 **小版本升级**，并记录 [变更记录](../README.md#维护约定) 中的模板说明。

---

## 7. 发版与回滚

### Q7.1 推荐发版顺序？

通用顺序：**备份数据库 → 停写或只读（若可）→ 迁移 → 部署新版本 → 冒烟测试 → 放开流量**。细节见 [部署总览](../04-deployment/01-deployment-overview.md) 与 [事件响应](../09-operations-maintenance/04-incident-handling.md)。

### Q7.2 回滚后数据不一致？

若新版本已执行 **不可逆迁移**，则 **不能** 仅回滚代码；需要 **数据修复脚本** 或 **从备份恢复**。发版前务必评估迁移可逆性。

---

## 8. 与业务 FAQ 的交界

### Q8.1 用户报「业务数据错了」，运维第一步做什么？

区分 **系统缺陷** 与 **操作错误**：先取 **单号、截图、时间、账号**，查 **操作日志** 与 **应用日志**。若属权限或会话问题，转 [登录权限 FAQ](01-login-permission-and-session-faq.md)；若属流程理解问题，转 [业务流程 FAQ](02-business-process-faq.md)。

### Q8.2 工标网爬取在生产失败，是否运维范畴？

若 **网络出口**、**DNS**、**TLS 中间人** 导致无法访问外网，属运维；若 **应用解析** 失败，属研发。参见 [标准爬取说明](../08-security-compliance/04-standards-crawl-metadata.md)。

---

## 延伸阅读

- [事件响应与通报](../09-operations-maintenance/04-incident-handling.md)
- [数据安全](../08-security-compliance/03-data-security.md)
- [调试手册（研发协助）](../03-development/05-debugging-playbook.md)

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版：运维 FAQ |

返回：[Wiki 首页](../README.md) · [登录权限 FAQ](01-login-permission-and-session-faq.md) · [业务流程 FAQ](02-business-process-faq.md)
