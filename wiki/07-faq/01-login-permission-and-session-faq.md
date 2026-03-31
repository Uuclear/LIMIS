# 登录、权限与会话 FAQ

本文汇总 LIMIS 中与 **登录认证**、**模块权限**、**JWT 与会话版本**、**菜单与路由权限** 相关的常见问题，并与知识库其他章节交叉引用。技术细节以当前代码实现为准。

**相关主文档**：[认证与 JWT](../05-api-and-integration/01-authentication-and-jwt.md) · [授权模型](../08-security-compliance/01-authorization-model.md) · [系统管理界面](../06-user-guide/06-system-administration-ui.md) · [前端请求信封](../05-api-and-integration/04-frontend-api-envelope.md) · [既有：权限排错](../03-admin-guides/03-permission-model-and-troubleshooting.md) · [既有：会话安全](../03-admin-guides/04-session-security-and-kickout.md)

---

## 目录

1. [登录与账号](#1-登录与账号)
2. [JWT、会话版本与「被踢下线」](#2-jwt会话版本与被踢下线)
3. [菜单、路由与模块权限](#3-菜单路由与模块权限)
4. [接口返回 401 / 403 时如何排查](#4-接口返回-401--403-时如何排查)
5. [与网关、代理相关的注意点](#5-与网关代理相关的注意点)

---

## 1. 登录与账号

### Q1.1 登录时提示「用户名或密码错误」，但密码确定没错？

可能原因包括：

- **大小写与空格**：用户名、密码是否多打了空格；密码是否区分大小写（取决于组织策略，系统底层校验为 Django 认证）。
- **账号被禁用**：后端对 `is_active=False` 的账号会拒绝登录并可能返回与密码错误相同的提示（避免枚举有效账号）。请管理员在 **系统管理 → 用户** 中检查账号状态，参见 [系统管理界面](../06-user-guide/06-system-administration-ui.md)。
- **登录失败锁定**：若在配置中启用了 `LOGIN_FAILURE_MAX_ATTEMPTS` 等，同一用户名 + IP 在窗口内失败次数过多会触发 **节流（Throttled）**，提示稍后再试。详见 [密码策略与登录节流](../03-admin-guides/05-password-policy-and-login-throttling.md) 与 [认证与 JWT](../05-api-and-integration/01-authentication-and-jwt.md)。

**建议**：由管理员核对账号状态与锁定策略；用户侧避免在多台设备上反复试错。

### Q1.2 登录成功后又立刻需要重新登录？

通常与 **Access Token 过期** 或 **会话版本（session_version）不一致** 有关，见 [§2](#2-jwt会话版本与被踢下线)。

若仅发生在某一浏览器：检查是否禁用 LocalStorage / 第三方 Cookie 策略导致刷新 Token 无法保存。

### Q1.3 忘记密码怎么办？

流程依赖现场策略：常见为管理员在 **用户管理** 中重置密码，或通过组织统一的 IAM/邮件重置。LIMIS 侧请查阅 [系统管理界面](../06-user-guide/06-system-administration-ui.md) 与 [管理员快速上手](../03-admin-guides/01-admin-overview-and-daily-checklist.md)。

---

## 2. JWT、会话版本与「被踢下线」

### Q2.1 系统里的「会话」和传统 Session Cookie 一样吗？

LIMIS API 侧主要使用 **JWT（Simple JWT）**：Access Token 用于请求鉴权，Refresh Token 用于刷新。与普通无状态 JWT 不同的是，系统在 Token 中携带 **`sv`（session_version）** 声明，并与数据库用户表中的 **`session_version` 字段** 对齐校验。

- 若数据库中的版本号 **大于** Token 中的 `sv`，校验失败，效果等价于 **「该用户所有已签发 Access/Refresh 一律作废」**。
- 典型触发：用户 **重新登录**、管理员执行 **踢出会话** 等会 **递增** `session_version` 的操作。

实现参考：`SessionVersionJWTAuthentication`、`SessionVersionRefreshToken`。详见 [认证与 JWT](../05-api-and-integration/01-authentication-and-jwt.md) 与 [既有：会话安全](../03-admin-guides/04-session-security-and-kickout.md)。

### Q2.2 为什么「改密码」或「管理员踢人」会导致所有人（或该用户）掉线？

这是 **设计行为**：通过递增 `session_version`，使旧 Token 全部失效，避免已泄露 Token 在密码变更后仍长期有效。

- **单用户被踢**：仅该用户的 `session_version` 变化，仅影响该账号。
- **若误以为「全员掉线」**：检查是否在运维操作中批量触发了用户更新、或网关/负载均衡层统一清除了客户端存储。

### Q2.3 多端同时登录是否允许？

默认 **允许**（未在 FAQ 层面禁止多设备）；每一端持有自己的 Token。若一端重新登录或管理员踢出，则 **所有端** 在下次请求校验失败时需重新登录。

若业务上要求「单端在线」，需在产品层增加策略（当前以会话版本递增实现「强制下线」为主）。

### Q2.4 Refresh Token 刷新失败，提示缺少会话版本或会话失效？

可能原因：

1. **用户 `session_version` 已在服务端递增**（重新登录、踢出等），旧 Refresh 携带的 `sv` 不再匹配。
2. **Token 被加入黑名单**（若启用 `token_blacklist` 应用）且已轮换失效。
3. **时钟偏差过大**：JWT `exp` 校验失败（少见，需校时）。

处理：**重新登录**。若频繁发生，抓包看 `/token/refresh/` 请求体与响应，并对照服务端日志。

---

## 3. 菜单、路由与模块权限

### Q3.1 登录成功但左侧菜单很少，或点开某页提示无权限？

LIMIS 前端根据 **路由元信息** 与当前用户 **权限列表** 过滤菜单（见前端 `permission` 工具与侧边栏逻辑）。后端则通过 **`LimsModulePermission`** 与 ViewSet 上的 **`lims_module`**、HTTP 方法映射的 `view/create/edit/delete` 做校验。

可能情况：

- **角色未分配**：用户未绑定角色，或角色未包含所需模块权限。请在 **系统管理 → 角色 → 分配权限** 中配置，参见 [授权模型](../08-security-compliance/01-authorization-model.md)。
- **超级用户**：`is_superuser` 通常绕过模块校验（以后端实现为准），但仍需登录有效 Token。
- **仅菜单隐藏**：直接输入 URL 仍可能 403——说明 **路由级** 与 **API 级** 均需权限。

### Q3.2 「无此模块操作权限」来自哪里？

该文案对应后端 `LimsModulePermission.message`。表示当前用户对当前接口所属 **模块** 的 **动作**（如 `view`、`edit`）未授权。需调整角色权限或联系管理员，而非清空浏览器缓存。

### Q3.3 前端能看到页面，但一保存就 403？

常见于 **GET 有 view**，但 **POST/PATCH 需要 create/edit**。请核对角色是否包含对应模块的写权限；开发环境可在浏览器网络面板查看失败请求的 Method 与 URL，对照后端 ViewSet 的 `lims_module` 与 `lims_action_map`。

---

## 4. 接口返回 401 / 403 时如何排查

| 现象 | 优先检查 |
|------|----------|
| 401 Unauthorized | Token 是否缺失、过期；`Authorization: Bearer` 格式是否正确；是否因 `sv` 不一致被判定为无效 Token |
| 403 Forbidden | 模块权限不足；是否为超级用户以外的业务规则拒绝 |
| 200 但业务 code 非成功 | 见 [错误响应与业务码](../05-api-and-integration/03-error-response-and-codes.md)，可能与网关改写 `code` 类型有关（字符串 `"200"` vs 数字 `200`） |

**前端开发** 请同时阅读 [前端请求信封](../05-api-and-integration/04-frontend-api-envelope.md)，避免未解包 `data` 导致界面「像没权限」实际是未取到数据。

---

## 5. 与网关、代理相关的注意点

### Q5.1 经 API 网关后，统一响应里的 `code` 变成字符串？

部分网关会把 JSON 中的数字转为字符串。前端请求层应对 **成功码兼容数字与字符串**（项目内 `request.ts` 约定），否则无法解包 `data`，界面表现为部分字段 `undefined`。详见 [前端请求信封](../05-api-and-integration/04-frontend-api-envelope.md) 与 [API 约定与信封](../05-api-docs/01-api-conventions-and-envelope.md)。

### Q5.2 反向代理未传递 `Authorization`？

会导致所有请求 401。请确认 Nginx/网关未剥离该头；HTTPS 终止后转发到上游时保留头信息。参见 [反向代理与 TLS](../04-deployment/04-reverse-proxy-and-tls.md)。

### Q5.3 真实 IP 与登录锁定

登录失败计数可能按 **用户名 + 客户端 IP** 维度。若代理未正确配置 `X-Forwarded-For`，可能表现为 **同一出口 IP 下多用户互相影响** 或 **锁定维度异常**。运维需核对 [部署与配置](../04-deployment/03-configuration-and-secrets.md)。

---

## 延伸阅读

- [运维 FAQ：会话与登录相关故障](03-operation-and-maintenance-faq.md)（值班视角）
- [数据安全](../08-security-compliance/03-data-security.md)
- [Git 与协作](../03-development/04-git-workflow.md)（若涉及权限配置变更的评审）

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版：登录、JWT、会话版本、权限与网关 FAQ |

返回：[Wiki 首页](../README.md) · [业务流程 FAQ](02-business-process-faq.md) · [运维 FAQ](03-operation-and-maintenance-faq.md)
