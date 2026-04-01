# 备份与恢复

- **数据库**：逻辑备份（`pg_dump` 等）按 RPO 调度；异地副本。
- **媒体文件**：附件与报告文件存储需一并备份。
- **恢复演练**：每季度至少一次。

值班：[运维 FAQ](../07-faq/03-operation-and-maintenance-faq.md) · [数据库运维](../09-operations-maintenance/03-database-operations.md)

---

## PostgreSQL（limis 库）逻辑备份与恢复示例

默认库名与用户见 `docker-compose.yml` 中 **`DB_NAME` / `DB_USER`**（未设置时多为 **`limis` / `limis`**）。以下为 **手工命令示例**，非定时任务脚本。

**环境变量（备份前确认）**：`DB_NAME`、`DB_USER`、`DB_PASSWORD`；宿主机连接 Compose 映射端口时常为 **`127.0.0.1:5434`**（以 `docker-compose.yml` `ports` 为准）。

**在 db 容器内备份（SQL 明文）**：

```bash
docker compose exec -T db pg_dump -U limis limis > limis_backup_$(date +%Y%m%d).sql
```

**在 db 容器内备份（自定义格式，便于 `pg_restore`）**：

```bash
docker compose exec -T db pg_dump -U limis -Fc limis > limis_backup_$(date +%Y%m%d).dump
```

**恢复（新库或覆盖前请先停写并自行评估风险）**：

- 明文 SQL：`docker compose exec -T db psql -U limis -d limis < limis_backup_YYYYMMDD.sql`
- 自定义格式：`docker compose exec -T db pg_restore -U limis -d limis --clean --if-exists - < limis_backup_YYYYMMDD.dump`（`-` 表示从标准输入读；参数按现场是否清空目标库调整）

宿主机若已安装 `psql`/`pg_dump`，也可对 **`localhost:5434`** 使用相同库名用户执行 `pg_dump` / `psql` / `pg_restore`。

更完整的 SOP 见 [备份与恢复标准操作](../03-admin-guides/09-backup-and-restore-sop.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.1 | Wiki | 补充 limis 库 pg_dump / 恢复示例 |
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
