# 运行时与进程模型

- **Web 进程**：Gunicorn/uWSGI 等多 worker；worker 数与 CPU、内存平衡。
- **异步任务**：若使用 Celery，另配 worker 与 broker（Redis/RabbitMQ）。
- **静态文件**：由 Nginx 直接服务或通过 CDN。

监控 [日志与监控](../09-operations-maintenance/02-logs-and-monitoring.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
