# 前端扩展指南（Vue 3 + TypeScript）

## 目录与职责

| 路径 | 说明 |
|------|------|
| `frontend/src/views/` | 页面级组件，按业务域分子目录（`projects`、`commissions`、`testing` 等） |
| `frontend/src/router/` | 路由；`index.ts` 汇总；`modules/*.ts` 按模块拆分 |
| `frontend/src/api/` | 对后端 REST 的封装（axios 实例、URL 路径） |
| `frontend/src/stores/` | Pinia 状态（如 `user.ts`） |
| `frontend/src/utils/` | 工具：`request.ts`（拦截器、幂等键）、`auth.ts`、`permission.ts`、`apiField.ts` 等 |
| `frontend/src/components/` | 可复用组件（如 `Layout`） |
| `frontend/src/types/` | TypeScript 类型定义 |
| `frontend/src/composables/` | 组合式函数 |

路径别名 **`@`** → `src`（`vite.config.ts`）。

---

## 规范

### 1. 命名与风格

- 组件文件：**PascalCase**，如 `CommissionList.vue`。
- 组合式 API：优先 `<script setup lang="ts">`。
- API 函数：语义化命名，与后端资源对齐（如 `fetchCommissionList`）。

### 2. HTTP 请求

统一使用 **`frontend/src/utils/request.ts`** 导出的 axios 实例：

- **`baseURL: '/api'`**，实际请求为 `/api/v1/...`（注意与 Vite 代理配合）。
- 自动附加 **`Authorization: Bearer <access>`**（`utils/auth.ts`）。
- 对 **POST/PUT/PATCH/DELETE**（除登录、刷新路径）自动添加 **`Idempotency-Key`**，与后端幂等中间件一致。

### 3. 响应体与信封

拦截器行为要点：

- 若 JSON 含 **`code`** 且为 **200 / 201**（含字符串 `"200"`），则 resolve 为 **`data`** 字段内容（若存在），否则为整包。
- **无 `code` 字段** 的响应（如登录返回 `access`/`refresh`）整包返回。

因此调用分页接口时，业务代码拿到的常是：

```ts
{ count, page, page_size, results }
```

集成爬虫、工标网等接口时，若存在 **`data` 嵌套**，使用 **`unwrapCrawlPayload`**（`utils/apiField.ts`）与 **`apiField`** 双读 snake_case / camelCase。

### 4. 路由与权限

- 路由 `meta.permission` 与 **`utils/permission.ts`**、`stores/user` 中的权限列表配合，控制菜单与进入页面。
- 全局路由守卫会 **`ensureProfile()`** 拉取 `/system/me/`，避免刷新后权限为空。

新增业务页面时：

1. 在 `views/<domain>/` 增加页面组件。
2. 在 `router/modules/<domain>.ts` 注册路由及 `meta.title` / `meta.permission`。
3. 若侧栏由 `Sidebar.vue` 维护，同步增加菜单项（按现有模式）。

### 5. 示例：新增只读列表页

1. `views/example/ExampleList.vue`：表格 + `onMounted` 调 `api/example.ts` 中 `listExamples`。
2. `api/example.ts`：

```ts
import request from '@/utils/request'

export function listExamples(params?: Record<string, unknown>) {
  return request.get('/v1/examples/', { params })
}
```

3. `router/modules/example.ts` 导出 `RouteRecordRaw[]`，并在 `router/index.ts` 中 `import` 与展开。

---

## 与后端字段约定

- 列表查询参数与 DRF `filter` / `search` / `ordering` 对齐。
- 日期提交格式与后端 `DateField`/`DateTimeField` 一致（常用 ISO 字符串）。
- 上传文件使用 `FormData` 与对应 `Content-Type`（勿被默认 JSON 拦截器误用）。

---

## 构建与本地命令

| 命令 | 作用 |
|------|------|
| `npm run dev` | Vite 开发服务器 |
| `npm run build` | `vue-tsc -b && vite build` 产出 `dist/` |

CI（`.github/workflows/frontend-ci.yml`）还会执行 `npm run type-check`、`npm run lint`（若 `package.json` 未定义脚本需补齐或调整 CI）。

---

## 提交流程建议

1. 在功能分支开发，保持单次 MR 目标单一。
2. 提交前本地 **`npm run build`**，确保类型与打包通过。
3. 与 UI 规范保持一致：Element Plus 组件、现有布局与间距习惯。
4. MR 描述中说明：路由/权限变更、是否依赖后端迁移或新环境变量。

---

## 注意事项

- 不要在页面中手写完整 API 根路径时忽略 **`/api`** 与 **`/v1`** 前缀的一致性。
- 令牌仅存 **`localStorage`** 时，注意 XSS 风险；生产应配合 CSP、依赖审计与 HTTPS。
- 大列表注意分页与后端 `page_size` 上限（默认最大 100）。
