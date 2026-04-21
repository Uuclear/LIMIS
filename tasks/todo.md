# Todo

- [x] 定位并修复 `seed_full_workflow --clear` 崩溃（`TestMethod` 已移除后的兼容问题）
- [x] 重新执行迁移与全流程种子，确认可重复初始化
- [x] 启动 backend/frontend 本地服务并执行循环 E2E 冒烟（登录、`/me`、dashboard）
- [x] 固化可重复执行脚本 `scripts/e2e_smoke.py`

## Review

- 本轮根因：演示数据脚本仍依赖旧模型 `TestMethod` 与相关字段，导致初始化阶段直接失败，阻断 E2E。
- 修复后验证：`seed_full_workflow --clear` 成功；E2E 循环 3 轮通过。
