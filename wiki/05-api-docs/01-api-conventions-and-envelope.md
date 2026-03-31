# API 约定与响应信封

本文档说明 LIMIS 后端（Django + Django REST framework）对外 HTTP API 的通用约定，与仓库实现一致。

## 基础信息

| 项目 | 说明 |
|------|------|
| API 前缀 | `/api/v1/` |
| 内容类型 | `application/json`（文件上传除外） |
| 认证 | 除登录、刷新令牌等白名单接口外，请求头需携带 JWT：`Authorization: Bearer <access_token>` |
| OpenAPI | `/api/schema/`（原始 Schema）；`/api/docs/`（Swagger UI）；`/api/redoc/`（ReDoc） |

各业务模块挂载在 `api/v1/<模块>/` 下，例如 `system`、`projects`、`commissions` 等（见根路由 `backend/limis/urls.py`）。

## 成功响应：业务信封 `{ code, message, data }`

多数列表（分页）、写操作及部分自定义接口采用统一业务信封：

```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

- **`code`**：业务状态码，成功时常见为 **`200`**（查询/更新/删除成功）或 **`201`**（创建成功）。类型应为数字；若经网关被序列化为字符串（如 `"200"`），前端 `frontend/src/utils/request.ts` 会兼容解析后再解包 `data`。
- **`message`**：人类可读说明。
- **`data`**：实际载荷（对象、列表或分页结构）。

### 分页列表（`StandardPagination`）

列表且启用分页时，`data` 为分页对象：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 135,
    "page": 1,
    "page_size": 20,
    "results": [ ]
  }
}
```

查询参数：

- `page`：页码（从 1 开始）
- `page_size`：每页条数（上限 100，见 `backend/core/pagination.py`）

### 创建 / 更新（`BaseModelViewSet`）

继承 `core.views.BaseModelViewSet` 的 ViewSet 对 **create / update** 返回信封；**destroy** 返回 `code: 200` 与固定文案。

**创建成功（HTTP 201）示例：**

```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 42,
    "name": "示例项目"
  }
}
```

**更新成功（HTTP 200）示例：**

```json
{
  "code": 200,
  "message": "更新成功",
  "data": { }
}
```

**删除成功（软删或硬删，HTTP 200）示例：**

```json
{
  "code": 200,
  "message": "删除成功"
}
```

### 非信封响应（需注意）

以下场景**不**使用 `{ code, message, data }` 三层结构，返回体为 DRF 默认或自定义扁平 JSON：

- **登录** `POST /api/v1/system/login/`：返回 `access`、`refresh`、`user`（见《认证与令牌》文档）。
- **当前用户** `GET /api/v1/system/me/`：直接返回用户序列化字段 + `permissions` 数组。
- **登出、改密** 等：常见为 `{ "detail": "..." }`。
- **单条资源 GET（retrieve）**：多数 ViewSet 未统一包信封，直接为资源 JSON 对象。
- **SimpleJWT 刷新**：`POST /api/v1/system/token/refresh/` 返回 `access`（及轮换时的 `refresh`），见 simplejwt 默认行为。

前端 Axios 拦截器仅当响应体含 **`code` 字段** 时按信封解析；否则将整个 body 当作业务数据返回。集成新接口时务必区分「信封接口」与「裸 JSON」。

## 错误响应

全局异常处理：`core.exceptions.custom_exception_handler`。

### 标准错误体

```json
{
  "code": 422,
  "message": "字段说明：第一条可读错误",
  "errors": { }
}
```

- **`code`**：可与 HTTP 状态码一致（如 400、403、404、422）；也用于业务异常自定义码。
- **`message`**：主错误信息；校验类错误会尽量拼接「字段名 + 首条说明」便于前端直接展示。
- **`errors`**：可选。存在时多为 DRF `ValidationError` 的 `detail` 结构（字段级错误字典或列表）。

HTTP 状态码通常与 `code` 对齐（见 `_build_error_response`）；若 `code` 非合法 HTTP 码会回退为 400。

### 常见 HTTP 状态

| 状态 | 含义 |
|------|------|
| 400 | 错误请求、业务异常（`BusinessException`） |
| 401 | 未认证或令牌无效（JWT / 会话版本不一致等） |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 幂等冲突等（见下） |
| 422 | 数据校验失败（含 `errors`） |
| 429 | 限流（如修改密码） |

### 仅含 `detail` 的 DRF 风格

部分视图仍直接返回 `{"detail": "..."}`（未经过统一 `code` 包装）。前端在 Axios 错误回调中会尝试读取 `detail` 或 `message`。

## 幂等请求头 `Idempotency-Key`

对 `POST` / `PUT` / `PATCH` / `DELETE` 且路径以 `/api/v1/` 开头的请求，可携带：

```http
Idempotency-Key: <uuid 或客户端生成的唯一字符串，建议 ≤128 字符>
```

中间件 `core.middleware.IdempotencyMiddleware` 会按用户 + 方法 + 路径 + 键去重；重复成功请求可重放缓存的响应（响应头 `X-Idempotency-Replayed: true`）。冲突时可能返回：

```json
{
  "code": 409,
  "message": "幂等键已被不同请求体占用"
}
```

登录与刷新令牌路径不参与幂等键逻辑（与前端 `frontend/src/utils/request.ts` 中跳过规则一致）。

## 模块权限（`LimsModulePermission`）

需登录的 ViewSet 常设置：

- `lims_module`：模块编码（如 `system`、`project`、`commission`）。
- `lims_action_map`：自定义 action 到权限动作（`view` / `create` / `edit` / `delete`）的映射。

未配置 `lims_module` 时仅校验是否登录。超级用户绕过模块校验。详见 `backend/core/permissions.py`。

## 与前端协作要点

1. **信封解包**：成功且 `code` 为 200/201 时，拦截器返回 **`data`**（若存在），调用方拿到的已是内部载荷。
2. **字符串 `code`**：网关若将 `code` 改为字符串 `"200"`，仍需能解包（项目已处理）。
3. **嵌套 `data`**：爬虫等接口可能出现 `data` 内再包一层，前端可用 `frontend/src/utils/apiField.ts` 中的 `unwrapCrawlPayload` 等工具剥层。
4. **snake_case / camelCase**：后端序列化多为 **snake_case**；若某处为 camelCase，读取字段时建议双读兼容（见 `apiField`）。

## 参考代码路径

| 内容 | 路径 |
|------|------|
| 根路由 | `backend/limis/urls.py` |
| 统一分页信封 | `backend/core/pagination.py` |
| CRUD 信封 | `backend/core/views.py`（`BaseModelViewSet`） |
| 异常格式 | `backend/core/exceptions.py` |
| 幂等与审计中间件 | `backend/core/middleware.py` |
| 前端 Axios 与信封 | `frontend/src/utils/request.ts` |
