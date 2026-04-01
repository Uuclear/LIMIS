# 日志与监控

- **应用**：结构化日志 + 请求 ID（若启用）。
- **Nginx**：访问与错误日志。
- **数据库**：慢查询、连接数。
- **告警**：5xx 率、延迟、磁盘、复制延迟。

与 [运维 FAQ](../07-faq/03-operation-and-maintenance-faq.md) 配合使用。

---

## 日志轮转（生产建议）

Linux 主机上建议使用 **logrotate**（或容器侧等价策略）避免单文件无限增长：

- **Gunicorn / Django**：`accesslog` / `errorlog` 指向 `/var/log/limis/` 下按日或按大小切割的文件；`logrotate` 配置示例：`daily`、`rotate 14`、`compress`、`copytruncate`（视进程是否支持 USR1 重开日志而定）。
- **Nginx**：`access_log` / `error_log` 同理；官方镜像常挂载卷并由宿主机 `logrotate` 管理。
- **Docker**：可将日志驱动设为 `json-file` 并限制 `max-size` / `max-file`，避免容器层日志撑满磁盘。

现场以运维规范为准；开发环境可仅 tail 控制台输出。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |
| 2026-04-01 | 1.1 | Wiki | 增补 logrotate / Docker 日志限制要点 |

返回：[Wiki 首页](../README.md)
