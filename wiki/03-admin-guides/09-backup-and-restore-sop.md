# 备份与恢复标准操作（SOP）

本文基于仓库默认技术栈（**PostgreSQL、Redis、MinIO、Django 媒体卷**）给出备份与恢复要点；生产环境应结合贵方备份平台细化 RPO/RTO。

## 1. 备份范围

| 组件 | 内容 | 典型位置 |
|------|------|----------|
| PostgreSQL | 业务全库 | `docker-compose.yml` 中 `postgres_data` 卷 |
| Redis | 缓存、登录计数、Celery broker | `redis_data`；**一般可重建**，不必作为唯一恢复源 |
| MinIO | 对象存储桶 | `minio_data` |
| Django `media` | 用户上传文件 | `media_data` 卷（compose 中 backend 挂载） |

**配置与密钥**：单独保管 `.env`、K8s Secret，不依赖数据库。

## 2. PostgreSQL 备份步骤（逻辑备份示例）

```
[1] 选择维护窗口，通知业务
    ↓
[2] 在容器或宿主机执行 pg_dump
    pg_dump -h <host> -U <user> -d <db> -Fc -f limis_$(date +%F).dump
    ↓
[3] 校验备份文件大小与 pg_restore --list
    ↓
[4] 异地复制/加密归档
```

**频率**：日全量 + 连续 WAL 归档（若启用 PITR）。

## 3. 恢复步骤（概要）

```
[1] 停应用与 Celery（避免写入）
    ↓
[2] 新建空库或 drop 后重建（谨慎）
    ↓
[3] pg_restore 导入
    ↓
[4] 恢复 MinIO 与 media 卷到一致时间点
    ↓
[5] migrate（若备份已含 schema 通常可跳过；以实际为准）
    ↓
[6] 启动应用，冒烟测试登录 / 关键 API
```

## 4. MinIO 与媒体文件

- 使用 `mc mirror` 或厂商备份工具同步桶与本地 `media`。
- 恢复后检查 **文件 URL** 与 `MEDIA_ROOT` 配置一致。

## 5. 风险

| 风险 | 说明 |
|------|------|
| 只恢复库不恢复对象 | 报告附件、头像等 404 |
| Redis 当主存 | 会话/限流可丢；用户需重登 |
| 跨版本恢复 | Django 迁移版本需与代码 tag 对齐 |

## 6. 回滚

备份恢复本身即是「回滚到某时间点」；**向前回滚**（撤销一次失败发布）优先用 **发布前快照** 而非手工删表。

## 7. 相关配置

- `DATABASES`、`MINIO_*`、`MEDIA_ROOT`：`backend/limis/settings/base.py`
- 卷定义：`docker-compose.yml`
