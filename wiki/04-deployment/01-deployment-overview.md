# 部署总览

生产环境常见形态：**Linux 主机** 或 **容器** + **进程管理器（systemd/supervisor）** + **Nginx** 反向代理 + **HTTPS**。

部署步骤纲要：

1. 准备数据库与密钥
2. 构建前端静态资源并同步
3. 收集静态文件、执行迁移
4. 启动 ASGI/WSGI 工作进程
5. 配置 Nginx 与 TLS

详见 [运行时](02-runtime-and-process.md)、[备份](05-backup-and-recovery.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
