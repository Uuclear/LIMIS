# 授权模型与模块权限

## LimsModulePermission

ViewSet 上设置 `lims_module`（如 `commission`），HTTP 方法映射为 `view/create/edit/delete`；`@action` 可通过 `lims_action_map` 覆盖。

超级用户 `is_superuser` 通常全部通过。

## 用户侧

用户通过 **角色** 关联 **权限** 列表；登录后权限注入前端用于菜单与按钮。

排错：[登录 FAQ](../07-faq/01-login-permission-and-session-faq.md) · [既有：权限排错](../03-admin-guides/03-permission-model-and-troubleshooting.md)

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
