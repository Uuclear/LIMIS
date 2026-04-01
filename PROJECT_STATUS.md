# Limis 实验室信息管理系统 - 项目状态文档（详细分层版）

**更新时间**：2026年4月1日（二次修订）  
**当前环境**：Django 5.x + Vue 3 + TypeScript + PostgreSQL + Redis（**本地开发**与 **Docker Compose** 两种跑法并存）  
**访问地址**  
- **Docker（推荐联调）**：`http://<主机IP>/`（Nginx **80**，API 同源 `/api/`；后端容器内 Gunicorn **8000** 仅集群内访问）  
- **本地 Vite 开发**：`frontend/vite.config.ts` — 前端 **3000**，`/api` 代理到本机 **8000**；后端 `runserver` 需 `DJANGO_SETTINGS_MODULE=limis.settings.dev`  
**Compose 说明**：`docker-compose.yml` 中 `backend` / `celery` / `celery-beat` 使用 **`limis.settings.dev`**；数据库对外映射 **5434→5432**（避免与本机 PostgreSQL 默认 5432 冲突）  
**管理员账号**：新库需 `createsuperuser` 或种子命令创建；演示数据与密码约定见 `docs/QUALITY_AND_ROADMAP.md`

---

## 0. 给后续 Agent 的快速导读（30 秒）

| 维度 | 要点 |
|------|------|
| **技术栈** | Django REST + JWT；Vue3 + Vite + TS + Element Plus + Pinia；业务信封：仅当响应 JSON 的 **`code` 为数字** 时解包 `data`（见 `frontend/src/utils/request.ts`）。 |
| **权限** | 后端 `LimsModulePermission` + 各 `ViewSet.lims_module`；`User.has_lims_permission`；权限表种子 `system/migrations/0002_seed_permissions.py`。 |
| **易踩坑** | 业务对象上的字段名 **`code`**（如项目编号）勿与统一响应 **`code: 200`** 混淆——已通过「数字型 code」判断规避。 |
| **待迁库** | 若拉取最新代码：`migrate` **system**（权限种子）、**testing**（`RecordTemplate.test_parameter`，见 `testing/migrations/0002_*.py`）、**standards**（`replaced_case` 等，以仓库为准）。 |

---

## 1. 近期进展摘要（2026-03）

### 1.1 较早批次（RBAC / 质量 / 标准等）

| 方向 | 说明 |
|------|------|
| 统一响应与 Axios | 仅当 `code` 为**数字**时按业务信封解析，避免与业务字段 **`code`（如项目编号）** 冲突，修复项目详情「基本信息」空白等问题。 |
| RBAC | `User.has_lims_permission` + `LimsModulePermission`；各业务 `ViewSet` 配置 `lims_module` / `lims_action_map`；迁移 **`0002_seed_permissions`** 预置权限并绑定默认角色。 |
| 角色管理 UI | 角色编辑使用 `/api/v1/system/permissions/grouped/` 按模块分组勾选；提交字段 **`permission_ids`**。 |
| 标准规范 | 附件重命名为「标准编号 + 扩展名」；`DEBUG` 下 `/media/` 由 Django 提供；工标网爬取与 `replaced_case` 等字段。 |
| 质量体系前端 | 内部审核、管理评审、不符合项、投诉等表单与后端字段对齐（含 `lead_auditor` 用户主键等）。 |
| 其他对齐 | 耗材/环境/人员等 API 路径与序列化器、委托/编号 `core_sequence` 兜底、登出携带 refresh 等。 |

### 1.2 末轮 UI/业务修复（便于 Agent 对需求）

| 方向 | 说明 |
|------|------|
| 顶栏铃铛 | `Header.vue`：`el-popover` 点击展开消息列表（当前为示例数据 + 路由跳转）；非静默角标。 |
| 用户管理 | API 增加 **`real_name`**（读写映射到 `first_name`）；**`role_ids`** 映射 `roles`；列表支持 **`real_name` 查询**；重置密码字段为 **`password`**；前端编辑只提交干净 payload。 |
| 仪器设备 | 列表行 **`manage_no`/`model_no`/`next_calibration_date`** 与表单字段 **`equipment_no`/`model`** 的映射与规范化，避免编辑时 `manage_no` 空值导致唯一约束 422；列表支持 **删除**；后端加强 **`manage_no`** 校验。 |
| 标准规范 | 列表 **删除** + `deleteStandard` API。 |
| 原始记录模板 | `RecordTemplate` 增加可选 **`test_parameter`**（`testing/migrations/0002_*`）；**`GET .../tasks/{id}/merged-record-schema/`** 按参数合并模板 schema；前端 **`/quality/record-templates`**（`RecordTemplateLibrary.vue`）+ 侧栏菜单项。 |

> **原始记录数据模型说明**：`OriginalRecord` 仍为 **单 `template` 外键**；合并接口用于 **预览/对接录入**——若产品要求「保存即合并结果」，需在创建原始记录时写入 `record_data`（可调用 `build_merged_record_schema_for_task` 的合并结果）。

### 1.3 2026-04 统计与工具链

| 方向 | 说明 |
|------|------|
| 多维统计 API | `tasks-by-project` / `tasks-by-method`；Dashboard 增加项目/方法任务数图；合格率饼图与后端 `category` 字段对齐。 |
| 样品标签 | 列表多选 + 批量打印二维码标签（print-js）。 |
| 前端规范 | ESLint 9 flat + `npm run lint`（`--quiet`）。 |

---

## 2. 关键路径速查（代码位置）

| 主题 | 路径提示 |
|------|----------|
| Axios 与信封 | `frontend/src/utils/request.ts` |
| 模块权限类 | `backend/core/permissions.py`（`LimsModulePermission`） |
| 用户序列化（real_name / role_ids） | `backend/apps/system/serializers.py` |
| 用户列表查询 real_name | `backend/apps/system/views.py` → `UserViewSet.get_queryset` |
| 顶栏 | `frontend/src/components/Layout/Header.vue` |
| 设备列表映射与删除 | `frontend/src/views/equipment/EquipmentList.vue`、`frontend/src/api/equipment.ts` |
| 标准删除 | `frontend/src/views/standards/StandardList.vue`、`frontend/src/api/standards.ts` |
| 合并原始记录 schema | `backend/apps/testing/services.py`（`build_merged_record_schema_for_task`）、`backend/apps/testing/views.py`（`merged_record_schema`） |
| 模板库页面与路由 | `frontend/src/views/quality/RecordTemplateLibrary.vue`、`frontend/src/router/modules/quality.ts` |
| 侧栏菜单 | `frontend/src/components/Layout/Sidebar.vue` |
| 统计多维接口 | `backend/apps/statistics/views.py`（`tasks-by-project` / `tasks-by-method`）、`frontend/src/api/statistics.ts` |

---

## 3. 系统基础架构（已完成）

### 3.1 项目初始化
- [x] Django 项目结构创建与 App 拆分（`apps/system`、`apps/projects`、`apps/commissions` 等）
- [x] Vue 3 + Vite + TypeScript 项目初始化
- [x] Element Plus + Pinia + Vue Router + Axios 集成
- [x] 统一的 `core/` 基础模块（BaseModel、权限中间件等）
- [x] 环境变量与配置文件管理（`DB_PASSWORD`、`DB_HOST` 等）

### 3.2 数据库与缓存
- [x] PostgreSQL 数据库创建与用户权限配置（用户 `limis`）
- [x] Redis 安装与基本连接测试
- [x] Django ORM 模型迁移（`makemigrations` + `migrate` 成功）
- [x] 数据库初始化脚本（初始管理员与测试用户）

### 3.3 开发与部署配置
- [x] Docker 与 docker-compose 全栈编排（`db` / `redis` / `minio` / `backend` / `frontend` / `celery` / `celery-beat`）
- [x] 后端容器：`migrate` + `collectstatic` + Gunicorn；**开发阶段**默认加载 **`limis.settings.dev`**
- [x] Vite 配置局域网访问（`host: '0.0.0.0'`，端口见 `vite.config.ts`）
- [x] Django runserver 绑定 `0.0.0.0:8000` 支持局域网访问（本地开发）
- [x] 前端 API 代理配置（`/api` 代理到后端 8000）；Docker 下由 **`nginx/nginx.conf`** 反代 `/api` 至 `backend:8000`

### 3.4 API 与中间件
- [x] DRF 框架集成与全局配置
- [x] 自定义 `AuditLogMiddleware`（解决 request.body 二次读取问题）
- [x] 全局异常处理与响应格式统一
- [x] CORS 与跨域配置
- [x] OpenAPI：`drf-spectacular`，开发环境可访问 **Swagger**（见 `README.md` / `api/docs/`）

---

## 4. 用户权限与认证系统（已完成 / 持续演进）

### 4.1 模型层
- [x] 自定义 `User` 模型（继承 AbstractUser，扩展手机号、部门、职称、头像）
- [x] `Role` 模型（11种实验室角色：admin、tech_director、quality_director、tester 等）
- [x] `Permission` 模型（动作级权限：view/create/edit/delete/approve/export）
- [x] `AuditLog` 操作审计日志模型
- [x] `BaseModel` 统一基础模型（创建/更新时间、软删除等）

### 4.2 后端认证与权限
- [x] JWT Token 认证（login / refresh / logout / me 接口）
- [x] 基于角色的权限控制（RBAC）+ **模块级 `lims_module` 校验**（`core.permissions.LimsModulePermission`）
- [x] 操作审计日志中间件（记录 POST/PUT/PATCH/DELETE 操作）
- [x] 敏感字段脱敏处理
- [x] 登录路径对齐（`/api/v1/system/login/`）
- [x] 权限数据种子：`system/migrations/0002_seed_permissions.py`（预置权限 + 默认角色分配）
- [x] 非超级管理员用户：**需在界面分配角色并重新登录**后，`/me` 返回的 `permissions` 才完整（运营说明，非缺陷）

### 4.3 前端认证
- [x] Pinia 用户状态管理（`stores/user.ts`）
- [x] Axios 请求拦截器（自动带 Token、统一错误处理；**数字型 `code` 信封**）
- [x] 登录页面与路由守卫
- [x] Token 自动刷新机制
- [x] 动态菜单与 **按钮级** `v-permission`：侧栏按路由 `meta.permission` 过滤（`Sidebar.vue` + `canAccessRoutePermission`）；主要业务页按钮已与种子权限码对齐（个别边角页仍以登录态为准时可按需补）

### 4.4 用户管理
- [x] 用户 CRUD 接口与序列化器
- [x] **列表/展示 `real_name`**；**创建/更新 `real_name`、`role_ids`** 与后端一致
- [x] 角色管理与权限分配页面（**按模块分组勾选权限**）
- [x] 初始数据脚本（创建 admin 及测试用户 zhangsan/lisi/wangwu）

---

## 5. 业务功能模块（已完成）

### 5.1 项目管理
- [x] `Project` 与 `SubProject` 模型
- [x] 项目 CRUD 接口
- [x] 前端项目管理页面（含参建单位、合同、见证人、统计等）

### 5.2 委托管理
- [x] `Commission` 模型 + 委托编号规则引擎
- [x] 委托状态流转（draft → pending_review → reviewed 等）
- [x] 委托管理前端页面（提交/评审与 **`commission:approve`** 权限码）

### 5.3 样品管理
- [x] `Sample` 模型 + 样品编号生成
- [x] 二维码生成与展示
- [x] 样品管理前端页面

### 5.4 检测业务
- [x] 检测任务管理后端
- [x] 原始记录模板（`RecordTemplate`；可关联 **检测方法** + 可选 **检测参数**）
- [x] **按检测任务合并参数模板 schema**（接口 + 服务层合并逻辑；前端模板库 + 预览）
- [x] 计算引擎与结果自动判定
- [x] 测试结果记录模型

### 5.5 报告与设备
- [x] 报告管理后端（`Report` 模型）
- [x] 仪器设备管理（`Equipment` 模型）；列表与表单字段映射、删除
- [x] 设备状态与校准记录

### 5.6 其他支持模块
- [x] 人员管理（`staff`）
- [x] 环境监控（`environment`）
- [x] 标准规范管理（`standards`）；列表删除
- [x] 质量管理体系（`quality`）
- [x] 耗材管理（`consumables`）
- [x] 统计分析服务（Dashboard、趋势图、合格率等）

---

## 6. 待完善与 Bug 修复清单（分层详细版）

### 6.1 高优先级 - 核心稳定性

#### 6.1.1 认证与安全
- [x] Logout 携带 refresh；后端对缺失 refresh 的容错
- [x] 多设备同时登录时的会话管理与踢出机制（2026-04-01 已完成：登录递增会话版本 + 管理员踢下线）
- [x] 前端 Axios 对 401 处理（登出/跳转登录）；**业务信封仅识别数字 `code`**
- [x] 密码修改接口的安全性验证（复杂度、频率；2026-04-01 已完成）
- [x] 登录失败次数限制与验证码功能（可选；2026-04-01 已完成登录失败限次，验证码按需后续接入）

#### 6.1.2 权限体系
- [x] 所有页面按钮级权限（`v-permission` 指令）与后端 `permission_code` 全量一致（2026-04-01 已完成全模块主要页面）
- [x] 动态路由与菜单根据权限自动生成（当前侧边栏多为静态；2026-04-01 已完成）
- [x] 后端视图集 `LimsModulePermission` + `lims_module`（主要业务已接入）
- [x] 超级管理员绕过权限（`is_superuser`）
- [x] 角色权限缓存优化（短时 TTL：`USER_PERMISSIONS_CACHE_SECONDS`，默认 120 秒；与 `session_version` 组合键）

#### 6.1.3 审计日志
- [x] AuditLog 中间件异常捕获是否过于宽泛（当前有 try/except；2026-04-01 已完成）
- [x] 日志查看页面与查询过滤功能（2026-04-01 已完成）
- [x] 敏感操作（如删除报告、修改结果）的强制记录（2026-04-01 已完成）
- [x] 日志导出与审计报表（2026-04-01 已完成 CSV 导出）

### 6.2 中优先级 - 业务完整性

#### 6.2.1 报告管理
- [x] 报告 PDF 导出（HTML 模板 + WeasyPrint；前端生成/预览下载）
- [ ] Word 模板引擎（Word 版式导出）
- [ ] 报告审批流（审核 → 技术负责人 → 授权签字人）与 UI 完全一致
- [ ] 电子签章与数字签名集成
- [ ] 报告预览页面（含二维码）
- [ ] 报告批量生成与导出

#### 6.2.2 打印与移动支持
- [x] 样品二维码批量打印功能（列表多选 + `getSampleLabel` + print-js；单次最多 30 条）
- [ ] 报告二维码防伪验证
- [ ] 移动端扫码查看样品/委托进度
- [x] 打印样式优化（`index.css` 中 `@media print`：侧栏/顶栏隐藏、主区全宽）

#### 6.2.3 数据统计与可视化
- [x] Dashboard 主页图表集成（ECharts：检测量、合格率、强度曲线、KPI）
- [x] 检测量趋势、合格率、强度曲线（`/v1/statistics/strength-curve/`）
- [x] 按时间、项目、检测项维度统计（时间：`test-volume` 的 `group_by` + `start_date`/`end_date`；项目/方法：`/v1/statistics/tasks-by-project/`、`tasks-by-method/`；合格率：按检测方法类别 `qualification-rate`；Dashboard 已展示项目/方法任务数柱状图）
- [x] 数据导出为 Excel（样品列表等已有导出；其它模块按需扩展）

#### 6.2.4 数据导入导出
- [ ] Excel 模板下载与批量导入（委托、样品）
- [x] 标准规范数据初始化脚本（`manage.py seed_site_lab_commercial_pack` 等含 `Standard` 与检测方法/参数种子；按需选用）
- [ ] 耗材入库/出库记录与库存预警
- [ ] 历史数据迁移工具

#### 6.2.5 检测原始记录（产品深化）
- [ ] 原始记录 **创建/保存** 时直接使用 **merged-record-schema** 结果填充 `record_data`（与当前单 `template` FK 策略统一）
- [ ] 模板库与「检测任务」页面联动（从任务跳转预览/录入）

### 6.3 低优先级 - 优化与扩展

#### 6.3.1 部署与运维
- [x] 生产环境配置（仓库已含 **Docker Compose** + `nginx/` 反代与 Gunicorn 镜像；上生产需按环境调 `DJANGO_SETTINGS_MODULE`、密钥与 HTTPS）
- [ ] 日志轮转与监控告警
- [ ] 数据库备份策略与恢复流程
- [ ] HTTPS 配置

#### 6.3.2 代码质量
- [ ] 单元测试覆盖率提升
- [x] API 接口文档（Swagger：`/api/docs/` + drf-spectacular）
- [x] 代码规范检查与 lint（`frontend/eslint.config.mjs` + `npm run lint` 使用 `--quiet` 保证零 error；存量 warning 可逐步收紧）
- [x] 前端类型检查脚本（`npm run typecheck` → `vue-tsc -b`，与 `build` 第一步一致）
- [ ] 类型提示完善（尤其是后端与部分前端模块）

#### 6.3.3 高级功能
- [ ] 通知中心（站内信、邮件、微信）— 顶栏当前为 **占位示例**
- [ ] 工作流引擎（更复杂的审批流）
- [ ] 移动端 H5 / 小程序适配
- [ ] AI 辅助检测结果分析（未来）

---

## 7. 使用说明与后续工作规范

1. **测试流程建议**
   - 先使用管理员账号完整走一遍委托→样品→检测→报告流程
   - 重点测试不同角色（tester、reviewer、quality_director）的权限差异
   - 记录所有前端报错、接口异常、权限失效问题

2. **后续开发规范**
   - 每次修改前请先更新本文件对应状态
   - 完成一个子任务后在 `[ ]` 改为 `[x]` 并注明完成时间
   - 重大 Bug 修复后在此文档中增加「已知问题已解决」说明

3. **文档维护**
   - 本文件为多 Agent 协同开发的「主要状态源」
   - 建议每周更新一次整体状态

---

**当前系统可正常启动并局域网访问**，已具备核心业务闭环能力；近期已覆盖 **权限与信封修复、用户/设备/标准关键交互、参数级原始记录模板与合并预览**。中长期仍建议优先完善 **报告审批与 Word 版式**、**多维度统计与报表**、**原始记录保存与合并策略统一**。

---

## 8. 下一步建议（精简）

1. **数据库**：`python manage.py migrate`（**system**、**testing**、**standards** 等以仓库迁移为准）。
2. **测试**：用户姓名/角色保存、设备编辑保存、标准/设备删除、模板库 CRUD、`merged-record-schema` 与任务 ID。
3. **产品**：报告审批链与 Word 导出、多维度统计、通知后端接口替换顶栏示例数据。

---

**后续 Agent 使用说明**：
- 本文档作为项目当前状态的主要记录；**优先阅读 §0、§1.2、§2**。
- 新功能开发前请先更新本文件
- 修复 Bug 后请在本文件对应条目打勾或增补 §1

---

*此文件由 AI 助手生成并维护，用于确保后续开发工作有序推进。*
