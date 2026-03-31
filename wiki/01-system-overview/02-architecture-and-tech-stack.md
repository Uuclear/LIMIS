# 架构与技术栈

## 适用对象

- 开发与运维人员：部署、排障、接口联调。
- 技术负责人：评估扩展点与安全边界。

## 前置条件

- 已阅读仓库根目录 `README.md` 中的环境与端口说明。
- 了解本系统为 **前后端分离**，浏览器只与前端静态资源及经 Nginx 反代的 API 交互。

## 页面入口（架构视角）

前端 **路由** 由 `frontend/src/router/index.ts` 聚合各模块子路由：

- 公共路由：`/login`。
- 主应用：`/` → `MainLayout`，子路由包含 `dashboard`、`system`、`project`、`entrustment`、`sample`、`equipment`、`staff`、`environment`、`quality`、`consumable`、`testing`、`reports` 等。
- 通配：未匹配路径重定向至 `/dashboard`（非登录页）。

**权限**：`router.beforeEach` 中调用 `getRoutePermission` + `canAccessRoutePermission`；无权限时提示并跳回 `/dashboard`。

| 层级 | 路径/组件 | 说明 |
|------|-----------|------|
| 布局 | `MainLayout.vue` | 侧栏 `Sidebar.vue` + 顶栏 + `<router-view>` |
| 菜单 | `Sidebar.vue` 中 `rawMenuItems` | 与业务路由一致，按权限过滤 |
| API | `frontend/src/utils/request.ts` | `baseURL: '/api'`，统一处理 `{ code, message, data }` 信封 |

## 字段说明

架构文档不定义业务字段；API 响应普遍采用：

```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

前端对 `code` **兼容数字与纯数字字符串**（如 `"200"`），避免网关改写类型导致不解包 `data`。

## 标准操作步骤（SOP）

### 本地开发

1. **后端**：`DJANGO_SETTINGS_MODULE=limis.settings.dev`，`migrations` 后 `runserver`（默认 8000）。
2. **前端**：Vite 开发服务器，将 `/api` 代理至后端（见 `frontend/vite.config.ts`）。
3. **鉴权**：登录获取 JWT，请求头 `Authorization: Bearer <token>`；401 时清除 token 并跳转 `/login`。

### 部署（Docker 概览）

1. 按 `README` 使用 `docker compose` 构建并启动。
2. 对外通常 **80** 为前端，**API 同域 `/api/`**；数据库、Redis、MinIO 等端口以 `docker-compose.yml` 为准。

### 排查接口问题

1. 浏览器 Network 查看响应体是否为信封格式。
2. 若前端拿不到业务数据，核对 `code` 类型与 `data` 嵌套（见 `apiField` / `unwrapCrawlPayload` 等业务规则）。
3. 后端模块权限：`LimsModulePermission` 与路由 `lims_module` 配置需一致。

## 常见错误

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 前端列表为空但 Network 200 | `code` 为字符串 `"200"` 旧逻辑未解包 | 已统一在 `request.ts` 处理，确认未使用绕过封装的请求 |
| 403/无权访问 | 用户角色未包含路由 `meta.permission` | 在系统管理配置角色权限 |
| 重复提交 | 写操作带 `Idempotency-Key` | 幂等设计，避免重复点击导致重复创建 |

## 数据核对清单

- [ ] 生产环境 `VITE_*` 或构建产物中 API 基路径与 Nginx `/api/` 一致。
- [ ] JWT 过期策略与前端 `handleUnauthorized` 行为符合安全要求。
- [ ] 后端 `StandardPagination` 分页返回 `data.results` 与前端列表解析一致。

## 与上下游模块关系

### 后端应用结构（概念）

- `apps/projects`：工程项目、参建单位、分部分项、合同、见证人。
- `apps/commissions`：委托单、委托项目行、合同评审。
- `apps/samples`：样品、样品组、处置。
- `apps/testing`：检测分类/方法/参数、任务 `TestTask`、原始记录 `OriginalRecord`、结果 `TestResult`、判定规则等。
- `apps/reports`：报告模板、报告、审批与发放。
- `apps/standards`：标准规范等（前端列表在 `/quality/standards`）。
- `apps/quality`：内审、管评、不符合项等。
- `apps/system`：用户、角色、审计日志等。

### 请求链路

```text
浏览器 → Nginx（静态 + /api 反代）→ Gunicorn/Django → PostgreSQL
                              ↓
                         JWT 中间件 / 权限
```

### 与前端路由的映射关系

每个业务模块的 **页面路由**（如 `/project`）通过 **API 客户端**（`frontend/src/api/*`）调用对应 **ViewSet**；权限字符串在路由 `meta.permission` 与后端模块权限中成对出现，部署与发版时需同步变更。
