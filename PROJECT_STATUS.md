# Limis 实验室信息管理系统 - 项目状态文档（详细分层版）

**更新时间**：2026年3月30日  
**当前环境**：开发模式（Django 5 + Vue 3 + TypeScript + PostgreSQL + Redis）  
**访问地址**：前端见 `frontend/vite.config.ts`（当前 **3000** 端口，`host: 0.0.0.0`）| 后端 **8000**（局域网示例：`http://<主机IP>:3000` / `:8000`）  
**管理员账号**：`admin` / `admin123`

---

## 0. 近期进展摘要（2026-03）

以下已在代码中落地，测试时请以当前仓库为准：

| 方向 | 说明 |
|------|------|
| 统一响应与 Axios | 仅当 `code` 为**数字**时按业务信封解析，避免与业务字段 **`code`（如项目编号）** 冲突，修复项目详情「基本信息」空白等问题。 |
| RBAC | `User.has_lims_permission` + `LimsModulePermission`；各业务 `ViewSet` 配置 `lims_module` / `lims_action_map`；迁移 **`0002_seed_permissions`** 预置权限并绑定默认角色。 |
| 角色管理 UI | 角色编辑使用 `/api/v1/system/permissions/grouped/` 按模块分组勾选；提交字段 **`permission_ids`**。 |
| 标准规范 | 附件重命名为「标准编号 + 扩展名」；`DEBUG` 下 `/media/` 由 Django 提供；工标网爬取与 `replaced_case` 等字段。 |
| 质量体系前端 | 内部审核、管理评审、不符合项、投诉等表单与后端字段对齐（含 `lead_auditor` 用户主键等）。 |
| 其他对齐 | 耗材/环境/人员等 API 路径与序列化器、委托/编号 `core_sequence` 兜底、登出携带 refresh 等。 |

---

## 1. 系统基础架构（已完成）

### 1.1 项目初始化
- [x] Django 项目结构创建与 App 拆分（`apps/system`、`apps/projects`、`apps/commissions` 等）
- [x] Vue 3 + Vite + TypeScript 项目初始化
- [x] Element Plus + Pinia + Vue Router + Axios 集成
- [x] 统一的 `core/` 基础模块（BaseModel、权限中间件等）
- [x] 环境变量与配置文件管理（`DB_PASSWORD`、`DB_HOST` 等）

### 1.2 数据库与缓存
- [x] PostgreSQL 数据库创建与用户权限配置（用户 `limis`）
- [x] Redis 安装与基本连接测试
- [x] Django ORM 模型迁移（`makemigrations` + `migrate` 成功）
- [x] 数据库初始化脚本（初始管理员与测试用户）

### 1.3 开发与部署配置
- [x] Docker 与 docker-compose 配置（文件存在但当前使用本地开发）
- [x] Vite 配置局域网访问（`host: '0.0.0.0'`，端口见 `vite.config.ts`）
- [x] Django runserver 绑定 `0.0.0.0:8000` 支持局域网访问
- [x] 前端 API 代理配置（`/api` 代理到后端 8000）

### 1.4 API 与中间件
- [x] DRF 框架集成与全局配置
- [x] 自定义 `AuditLogMiddleware`（解决 request.body 二次读取问题）
- [x] 全局异常处理与响应格式统一
- [x] CORS 与跨域配置
- [x] OpenAPI：`drf-spectacular`，开发环境可访问 **Swagger**（见 `README.md` / `api/docs/`）

---

## 2. 用户权限与认证系统（已完成 / 持续演进）

### 2.1 模型层
- [x] 自定义 `User` 模型（继承 AbstractUser，扩展手机号、部门、职称、头像）
- [x] `Role` 模型（11种实验室角色：admin、tech_director、quality_director、tester 等）
- [x] `Permission` 模型（动作级权限：view/create/edit/delete/approve/export）
- [x] `AuditLog` 操作审计日志模型
- [x] `BaseModel` 统一基础模型（创建/更新时间、软删除等）

### 2.2 后端认证与权限
- [x] JWT Token 认证（login / refresh / logout / me 接口）
- [x] 基于角色的权限控制（RBAC）+ **模块级 `lims_module` 校验**（`core.permissions.LimsModulePermission`）
- [x] 操作审计日志中间件（记录 POST/PUT/PATCH/DELETE 操作）
- [x] 敏感字段脱敏处理
- [x] 登录路径对齐（`/api/v1/system/login/`）
- [x] 权限数据种子：`system/migrations/0002_seed_permissions.py`（预置权限 + 默认角色分配）
- [ ] 非超级管理员用户：**需在界面分配角色并重新登录**后，`/me` 返回的 `permissions` 才完整；前端菜单/按钮仍可按需与 `permissions` 对齐

### 2.3 前端认证
- [x] Pinia 用户状态管理（`stores/user.ts`）
- [x] Axios 请求拦截器（自动带 Token、统一错误处理；**数字型 `code` 信封**）
- [x] 登录页面与路由守卫
- [x] Token 自动刷新机制
- [ ] 动态菜单与 **按钮级** `v-permission` 与后端 `permissions` 列表全量对齐（部分页面仍依赖「已登录」或角色判断）

### 2.4 用户管理
- [x] 用户 CRUD 接口与序列化器
- [x] 角色管理与权限分配页面（**按模块分组勾选权限**）
- [x] 初始数据脚本（创建 admin 及测试用户 zhangsan/lisi/wangwu）

---

## 3. 业务功能模块（已完成）

### 3.1 项目管理
- [x] `Project` 与 `SubProject` 模型
- [x] 项目 CRUD 接口
- [x] 前端项目管理页面（含参建单位、合同、见证人、统计等）

### 3.2 委托管理
- [x] `Commission` 模型 + 委托编号规则引擎
- [x] 委托状态流转（draft → pending_review → reviewed 等）
- [x] 委托管理前端页面（提交/评审与 **`commission:approve`** 权限码）

### 3.3 样品管理
- [x] `Sample` 模型 + 样品编号生成
- [x] 二维码生成与展示
- [x] 样品管理前端页面

### 3.4 检测业务
- [x] 检测任务管理后端
- [x] 原始记录模板引擎
- [x] 计算引擎与结果自动判定
- [x] 测试结果记录模型

### 3.5 报告与设备
- [x] 报告管理后端（`Report` 模型）
- [x] 仪器设备管理（`Equipment` 模型）
- [x] 设备状态与校准记录

### 3.6 其他支持模块
- [x] 人员管理（`staff`）
- [x] 环境监控（`environment`）
- [x] 标准规范管理（`standards`）
- [x] 质量管理体系（`quality`）
- [x] 耗材管理（`consumables`）
- [x] 统计分析服务（Dashboard、趋势图、合格率等）

---

## 4. 待完善与 Bug 修复清单（分层详细版）

### 4.1 高优先级 - 核心稳定性（必须优先解决）

#### 4.1.1 认证与安全
- [x] Logout 携带 refresh；后端对缺失 refresh 的容错
- [ ] 多设备同时登录时的会话管理与踢出机制
- [x] 前端 Axios 对 401 处理（登出/跳转登录）；**业务信封仅识别数字 `code`**
- [ ] 密码修改接口的安全性验证（复杂度、频率）
- [ ] 登录失败次数限制与验证码功能（可选）

#### 4.1.2 权限体系
- [ ] 所有页面按钮级权限（`v-permission` 指令）与后端 `permission_code` 全量一致
- [ ] 动态路由与菜单根据权限自动生成（当前侧边栏多为静态）
- [x] 后端视图集 `LimsModulePermission` + `lims_module`（主要业务已接入）
- [x] 超级管理员绕过权限（`is_superuser`）
- [ ] 角色权限缓存优化（可选）

#### 4.1.3 审计日志
- [ ] AuditLog 中间件异常捕获是否过于宽泛（当前有 try/except）
- [ ] 日志查看页面与查询过滤功能
- [ ] 敏感操作（如删除报告、修改结果）的强制记录
- [ ] 日志导出与审计报表

### 4.2 中优先级 - 业务完整性

#### 4.2.1 报告管理
- [ ] 报告模板引擎（支持 Word/PDF 导出）
- [ ] 报告审批流（审核 → 技术负责人 → 授权签字人）与 UI 完全一致
- [ ] 电子签章与数字签名集成
- [ ] 报告预览页面（含二维码）
- [ ] 报告批量生成与导出

#### 4.2.2 打印与移动支持
- [ ] 样品二维码批量打印功能
- [ ] 报告二维码防伪验证
- [ ] 移动端扫码查看样品/委托进度
- [ ] 打印样式优化（CSS @media print）

#### 4.2.3 数据统计与可视化
- [ ] Dashboard 主页图表集成（ECharts）
- [ ] 检测量趋势图、合格率统计、强度曲线
- [ ] 按时间、项目、检测项维度统计
- [ ] 数据导出为 Excel

#### 4.2.4 数据导入导出
- [ ] Excel 模板下载与批量导入（委托、样品）
- [ ] 标准规范数据初始化脚本
- [ ] 耗材入库/出库记录与库存预警
- [ ] 历史数据迁移工具

### 4.3 低优先级 - 优化与扩展

#### 4.3.1 部署与运维
- [ ] 生产环境配置（Gunicorn + Nginx + Supervisor / Docker）
- [ ] 日志轮转与监控告警
- [ ] 数据库备份策略与恢复流程
- [ ] HTTPS 配置

#### 4.3.2 代码质量
- [ ] 单元测试覆盖率提升
- [x] API 接口文档（Swagger：`/api/docs/` + drf-spectacular）
- [ ] 代码规范检查与 lint
- [ ] 类型提示完善（尤其是前端）

#### 4.3.3 高级功能
- [ ] 通知中心（站内信、邮件、微信）
- [ ] 工作流引擎（更复杂的审批流）
- [ ] 移动端 H5 / 小程序适配
- [ ] AI 辅助检测结果分析（未来）

---

## 5. 使用说明与后续工作规范

1. **测试流程建议**
   - 先使用管理员账号完整走一遍委托→样品→检测→报告流程
   - 重点测试不同角色（tester、reviewer、quality_director）的权限差异
   - 记录所有前端报错、接口异常、权限失效问题

2. **后续开发规范**
   - 每次修改前请先更新本文件对应状态
   - 完成一个子任务后在 `[ ]` 改为 `[x]` 并注明完成时间
   - 重大 Bug 修复后在此文档中增加「已知问题已解决」说明

3. **文档维护**
   - 本文件为多 Agent 协同开发的「唯一状态源」
   - 建议每周更新一次整体状态

---

**当前系统可正常启动并局域网访问**，已具备核心业务闭环能力；近期已加强 **权限种子数据、后端模块鉴权、角色权限 UI、Axios 与项目编号冲突修复**。中长期仍建议优先完善 **报告生成与审批体验**、**统计可视化**、**按钮级权限与菜单动态化**。

---

## 下一步建议（精简）

1. **部署**：`migrate` 应用含 `0002_seed_permissions`，确认非超管用户绑定角色后接口行为符合预期。
2. **测试**：委托提交/评审、项目详情、标准附件上传、质量模块新增、角色权限保存。
3. **产品**：报告 PDF/审批链、Dashboard 图表、导入导出。

---

**后续 Agent 使用说明**：
- 本文档作为项目当前状态的主要记录
- 新功能开发前请先更新此文档
- 修复 Bug 后请在此文档对应条目打勾

---

*此文件由 AI 助手生成并维护，用于确保后续开发工作有序推进。*
