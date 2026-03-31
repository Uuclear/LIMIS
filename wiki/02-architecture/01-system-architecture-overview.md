# 系统架构总览

LIMIS 采用 **前后端分离**：浏览器中的 **Vue 3 + TypeScript** 单页应用通过 **HTTPS** 调用 **Django REST Framework** API；认证使用 **JWT**，并辅以 **session_version** 实现服务端可控的会话失效。

```text
[浏览器 SPA] --HTTPS/JSON--> [Nginx/网关] --> [Gunicorn/uWSGI + Django]
                                                  |
                                                  v
                                            [PostgreSQL 等]
                                            [Redis 可选]
```

## 分层说明

| 层 | 职责 |
|----|------|
| 表现层 | 路由、权限指令、表单与列表 |
| API 层 | ViewSet、序列化、权限类 `LimsModulePermission` |
| 领域层 | 模型、服务、信号（按应用划分 apps.*） |
| 基础设施 | 数据库、缓存、文件存储 |

延伸阅读：[后端栈](02-backend-django-stack.md) · [前端栈](03-frontend-vue-stack.md) · [既有：架构与技术栈](../01-system-overview/02-architecture-and-tech-stack.md)

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
