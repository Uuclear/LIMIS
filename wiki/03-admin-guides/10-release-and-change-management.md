# 发布与变更管理

本文给出 LIMIS **发版检查清单**、与代码结构的对应关系，以及失败时的回滚思路。

## 1. 发布前检查清单

```
[1] 代码冻结：合并到发布分支，打 tag
    ↓
[2] 阅读 CHANGELOG / 迁移说明：是否有破坏性迁移
    ↓
[3] 备份：PostgreSQL + MinIO + media（见 09-backup-and-restore-sop.md）
    ↓
[4] 环境变量 diff：SECRET_KEY、DB、REDIS、MINIO、CORS、LOGIN_*
    ↓
[5] 执行 migrate
    ↓
[6] collectstatic（若使用静态文件）
    ↓
[7] 前端构建：npm ci && npm run build（路径以项目为准）
    ↓
[8] 灰度/金丝雀（可选）→ 全量
    ↓
[9] 冒烟：登录、/me、关键业务只读接口
```

## 2. 与仓库路径的对应

| 环节 | 路径 |
|------|------|
| 后端入口 | `backend/manage.py`、`backend/limis/wsgi.py` |
| URL 聚合 | `backend/limis/urls.py` |
| 设置 | `backend/limis/settings/base.py`、`dev.py` |
| 前端路由 | `frontend/src/router/index.ts` |
| Compose | `docker-compose.yml` |

## 3. API 兼容性

- 前端依赖 `code` + `data` 信封（见 `frontend/src/utils/request.ts`）；网关若改 `code` 类型需兼容。
- 新增 `Permission` 行：老用户需重新分配角色或跑数据迁移。

## 4. 变更类型与风险

| 变更 | 风险 | 建议 |
|------|------|------|
| 仅代码无迁移 | 低 | 常规回滚即可 |
| 迁移加字段 | 中 | 可逆迁移或双写期 |
| 迁移删字段/表 | 高 | 必须备份；先弃用再删 |

## 5. 回滚策略

1. **应用回滚**：部署上一镜像/tag。
2. **数据库**：若新迁移已执行且破坏性，用 **备份恢复** 或 **前向修复迁移**（数据团队决策）。
3. **会话**：发版可能涉及 JWT 密钥变更 → 全员重新登录；`session_version` 策略见 `04-session-security-and-kickout.md`。

## 6. 沟通与记录

- 记录变更窗口、负责人、影响模块（委托/检测/报告等）。
- 重大权限模型变更需同步培训（见 `03-permission-model-and-troubleshooting.md`）。
