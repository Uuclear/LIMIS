# LIMIS 系统开发任务拆分

> 每个任务均可独立开发，标注了依赖关系和所属阶段。
> 状态：[ ] 待做 | [~] 进行中 | [x] 完成

---

## 与仓库现状对照（2026-03）

以下为**对当前代码的摘要**，避免下文历史任务列表与真实进度混淆。细项仍以 `PROJECT_STATUS.md` 为准。

| 类别 | 状态 |
|------|------|
| 仓库骨架、Docker Compose、Nginx 反代、`settings` 分环境 | 已具备 |
| 后端 `apps/*` 业务模块、迁移、RBAC、JWT、审计中间件 | 已具备（持续迭代） |
| 前端 Vue3 + 路由 + 布局 + 主要业务页面 | 已具备（持续迭代） |
| 管理命令（`seed_demo_data`、`seed_full_workflow`、`seed_role_test_users` 等） | 已具备；**无** `init_data` |
| 生产级发布（`prod` 严格收紧、HTTPS、监控） | 未作为当前阶段目标 |

**下文各阶段任务**保留为「原始拆分与依赖参考」；若与上表冲突，**以上表与 `PROJECT_STATUS.md` 为准**。

---

## 第一阶段：基础框架 + 核心业务流（4周）

### 1.1 项目骨架搭建

- [ ] **T-1.1.1** 初始化Django项目结构
  - 创建 `backend/` 目录，执行 django-admin startproject limis
  - 配置 settings 分环境（base/dev/prod）
  - 文件：`backend/limis/settings/base.py`, `dev.py`, `prod.py`
  - 依赖：无

- [ ] **T-1.1.2** 初始化Vue 3前端项目
  - 使用 Vite 创建 Vue 3 + TypeScript 项目
  - 安装 Element Plus、Vue Router、Pinia、Axios
  - 文件：`frontend/` 目录
  - 依赖：无

- [ ] **T-1.1.3** Docker容器化配置
  - 编写 `backend/Dockerfile`（Python 3.12 + Django）
  - 编写 `frontend/Dockerfile`（Node 20 + Nginx）
  - 编写 `docker-compose.yml`（Django + PostgreSQL + Redis + MinIO + Nginx）
  - 编写 `nginx/nginx.conf`（前后端反向代理）
  - 编写 `.env`（数据库连接、密钥等环境变量）
  - 依赖：T-1.1.1, T-1.1.2

- [ ] **T-1.1.4** 数据库初始化与迁移框架
  - 配置 PostgreSQL 连接
  - 创建公共基类 Model（`backend/core/models.py`）：BaseModel（含created_at, updated_at, created_by等）
  - 配置 django-extensions、django-filter
  - 依赖：T-1.1.1

- [ ] **T-1.1.5** API基础框架配置
  - 配置 Django REST Framework（认证、分页、异常处理、API版本）
  - 创建 `backend/core/pagination.py`（统一分页器）
  - 创建 `backend/core/exceptions.py`（统一异常处理）
  - 创建 `backend/core/permissions.py`（权限基类）
  - 配置 Swagger/OpenAPI 文档（drf-spectacular）
  - 依赖：T-1.1.1

- [ ] **T-1.1.6** 前端基础框架搭建
  - 配置 Axios 请求拦截器（Token、错误处理）
  - 配置路由守卫（登录验证）
  - 创建统一布局组件（侧边栏 + 顶栏 + 内容区）
  - 创建公共组件：分页表格、搜索表单、确认对话框
  - 依赖：T-1.1.2

### 1.2 用户认证与权限（RBAC）

- [ ] **T-1.2.1** 用户模型与认证后端
  - 自定义 User Model（继承AbstractUser，扩展：手机号、部门、职称、头像）
  - JWT认证（djangorestframework-simplejwt）
  - 登录/登出/刷新Token接口
  - 文件：`backend/apps/system/models.py`, `views.py`
  - 依赖：T-1.1.4

- [ ] **T-1.2.2** 角色与权限模型
  - Role 模型（角色名、描述、权限列表）
  - Permission 模型（权限码、模块、操作类型）
  - 预置角色：系统管理员、技术负责人、质量负责人、授权签字人、报告审核人、质量监督员、检测人员、样品管理员、设备管理员、业务受理员
  - 文件：`backend/apps/system/models.py`
  - 依赖：T-1.2.1

- [ ] **T-1.2.3** 权限控制中间件
  - 基于角色的API权限校验
  - 数据权限隔离（按部门/项目）
  - 操作日志记录中间件（AuditLog自动记录）
  - 文件：`backend/core/permissions.py`, `backend/core/middleware.py`
  - 依赖：T-1.2.2

- [ ] **T-1.2.4** 前端登录与权限控制
  - 登录页面
  - Token管理（Pinia store）
  - 动态路由（基于角色权限过滤菜单）
  - 按钮级权限指令（v-permission）
  - 文件：`frontend/src/views/login/`, `frontend/src/stores/user.ts`
  - 依赖：T-1.1.6, T-1.2.1

- [ ] **T-1.2.5** 用户管理后台页面
  - 用户列表/新增/编辑/停用
  - 角色管理：角色列表/权限分配
  - 部门管理
  - 操作日志查询
  - 文件：`frontend/src/views/system/`
  - 依赖：T-1.2.4

### 1.3 工程项目管理模块

- [ ] **T-1.3.1** 项目数据模型
  - Project模型：名称、编号、地点、类型、状态、开工/竣工日期
  - Organization模型：参建单位（建设/施工/监理/设计/检测方）
  - SubProject模型：分部分项工程
  - Contract模型：检测合同
  - Witness模型：见证人信息
  - 文件：`backend/apps/projects/models.py`
  - 依赖：T-1.1.4

- [ ] **T-1.3.2** 项目API接口
  - CRUD接口（Project, Organization, SubProject, Contract, Witness）
  - 列表筛选/搜索/分页
  - 项目统计接口（关联委托数、样品数、报告数）
  - 文件：`backend/apps/projects/serializers.py`, `views.py`, `urls.py`
  - 依赖：T-1.3.1

- [ ] **T-1.3.3** 项目管理前端页面
  - 项目列表页（表格 + 搜索）
  - 项目详情页（基本信息 + 参建单位 + 分部工程 + 合同）
  - 项目新增/编辑表单
  - 见证人管理
  - 文件：`frontend/src/views/projects/`
  - 依赖：T-1.1.6, T-1.3.2

### 1.4 委托管理模块

- [ ] **T-1.4.1** 委托数据模型
  - Commission模型：委托编号、关联项目、施工部位、委托日期、状态（草稿/待审/已审/退回）
  - CommissionItem模型：委托检测项目明细（检测对象、检测参数、标准方法、数量）
  - ContractReview模型：合同评审记录
  - 文件：`backend/apps/commissions/models.py`
  - 依赖：T-1.3.1

- [ ] **T-1.4.2** 委托编号规则引擎
  - 可配置的编号规则（前缀 + 年份 + 分类代码 + 流水号）
  - 支持按项目/检测类别分别编号
  - 自动生成、防重复
  - 文件：`backend/core/utils/numbering.py`
  - 依赖：T-1.1.4

- [ ] **T-1.4.3** 委托API接口
  - 委托单CRUD
  - 委托审批流程接口（提交/审批/退回）
  - 合同评审接口
  - 委托单打印数据接口
  - 文件：`backend/apps/commissions/serializers.py`, `views.py`, `services.py`
  - 依赖：T-1.4.1, T-1.4.2

- [ ] **T-1.4.4** 委托管理前端页面
  - 委托单列表（多状态Tab切换）
  - 委托单创建表单（关联项目、添加检测项目明细）
  - 合同评审表单
  - 委托单详情与审批
  - 委托单打印预览
  - 文件：`frontend/src/views/commissions/`
  - 依赖：T-1.1.6, T-1.4.3

### 1.5 样品管理模块

- [ ] **T-1.5.1** 样品数据模型
  - Sample模型：编号、名称、规格型号、数量、状态（待检/检测中/已检/留样/已处置）、取样日期、送样日期、取样位置、见证人、见证标记
  - SampleGroup模型：组样（关联多个Sample，如混凝土3块一组）
  - SampleDisposal模型：样品处置记录
  - 文件：`backend/apps/samples/models.py`
  - 依赖：T-1.4.1

- [ ] **T-1.5.2** 样品编号与二维码
  - 样品自动编号（年份+类型代码+流水号）
  - 二维码生成（qrcode库）
  - 条码标签PDF生成（用于打印）
  - 盲样编号（隐去委托方信息的独立编号）
  - 文件：`backend/apps/samples/services.py`, `backend/core/utils/barcode.py`
  - 依赖：T-1.5.1

- [ ] **T-1.5.3** 样品API接口
  - 样品登记接口（含批量登记）
  - 样品状态流转接口
  - 样品查询（按编号/二维码扫码/委托单/状态）
  - 留样管理接口（到期提醒列表）
  - 样品处置接口
  - 样品台账导出
  - 文件：`backend/apps/samples/views.py`, `serializers.py`
  - 依赖：T-1.5.1, T-1.5.2

- [ ] **T-1.5.4** 样品管理前端页面
  - 样品登记表单（关联委托单自动填入）
  - 样品列表（状态筛选、二维码扫码搜索）
  - 样品流转时间线
  - 标签打印功能
  - 留样管理与到期提醒
  - 样品处置记录
  - 文件：`frontend/src/views/samples/`
  - 依赖：T-1.1.6, T-1.5.3

---

## 第二阶段：检测执行核心（4周）

### 2.1 检测任务管理

- [ ] **T-2.1.1** 检测任务数据模型
  - TestTask模型：关联样品/委托、检测项目、分配检测员、分配设备、计划检测日期、实际检测日期、状态（待分配/待检/检测中/已完成/异常）
  - TestCategory模型：检测类别字典（材料检测/混凝土/地基桩基/钢结构等）
  - TestProject模型：检测项目字典（关联标准方法、检测参数）
  - 文件：`backend/apps/testing/models.py`
  - 依赖：T-1.5.1

- [ ] **T-2.1.2** 任务分配引擎
  - 自动匹配算法：根据检测项目匹配有授权的人员+可用设备
  - 龄期计算服务：根据样品类型自动计算检测到期日（7d/28d/60d/90d）
  - 超期预警服务：Celery定时任务检查并通知
  - 文件：`backend/apps/testing/services.py`
  - 依赖：T-2.1.1

- [ ] **T-2.1.3** 检测任务API接口
  - 任务列表（按状态/人员/日期筛选）
  - 任务分配/重分配接口
  - 任务状态变更接口
  - 今日待检列表/龄期到期提醒列表
  - 文件：`backend/apps/testing/views.py`
  - 依赖：T-2.1.1, T-2.1.2

- [ ] **T-2.1.4** 检测任务前端页面
  - 任务看板（Kanban视图：待分配/待检/进行中/已完成）
  - 任务列表（表格视图 + 高级筛选）
  - 任务分配对话框（人员+设备选择）
  - 龄期日历视图（显示到期检测任务）
  - 超期预警弹窗
  - 文件：`frontend/src/views/testing/`
  - 依赖：T-1.1.6, T-2.1.3

### 2.2 原始记录模板引擎

- [ ] **T-2.2.1** 记录模板数据模型
  - RecordTemplate模型：模板名称、关联检测项目、版本号、模板定义（JSON Schema）
  - OriginalRecord模型：关联检测任务、模板版本、记录数据（JSON）、状态（草稿/待复核/已复核/退回）、电子签名
  - RecordRevision模型：记录修改历史（字段级变更追踪）
  - 文件：`backend/apps/testing/models.py`（追加）
  - 依赖：T-2.1.1

- [ ] **T-2.2.2** 动态表单JSON Schema设计
  - 定义通用字段类型：数值、文本、日期、选择、计算公式、表格
  - 预置模板：
    - 混凝土抗压强度原始记录
    - 钢筋拉伸试验原始记录
    - 水泥胶砂强度原始记录
    - 砂石级配试验原始记录
    - 标准贯入试验原始记录
  - 文件：`backend/apps/testing/schemas/`
  - 依赖：T-2.2.1

- [ ] **T-2.2.3** 原始记录API接口
  - 获取模板定义
  - 创建/保存原始记录（自动填入环境+设备信息）
  - 记录提交/复核/退回工作流
  - 修改追踪（对比差异）
  - 文件：`backend/apps/testing/views.py`（追加）
  - 依赖：T-2.2.1, T-2.2.2

- [ ] **T-2.2.4** 前端动态表单渲染组件
  - 根据JSON Schema动态渲染表单
  - 支持表格型数据录入（试验数据多行）
  - 自动填入关联信息（设备、环境、人员）
  - 数据暂存/提交
  - 文件：`frontend/src/components/DynamicForm/`
  - 依赖：T-1.1.6

- [ ] **T-2.2.5** 原始记录前端页面
  - 记录填写页面（嵌入动态表单）
  - 记录复核页面（对比视图、批注、签字）
  - 记录列表（按状态/项目筛选）
  - 记录打印预览
  - 文件：`frontend/src/views/testing/records/`
  - 依赖：T-2.2.4, T-2.2.3

### 2.3 计算引擎与结果判定

- [ ] **T-2.3.1** 数据修约模块
  - 实现 GB/T 8170 数值修约规则（四舍六入五成双）
  - 有效位数控制
  - 极端值剔除（格拉布斯/狄克逊准则）
  - 文件：`backend/core/utils/rounding.py`
  - 依赖：无

- [ ] **T-2.3.2** 计算公式引擎
  - 公式定义格式（支持变量引用、条件判断）
  - 预置公式库：
    - 混凝土抗压强度 = F / A（面积换算、尺寸修正系数）
    - 钢筋拉伸强度 = F_max / S0
    - 水泥胶砂强度（抗折/抗压）
    - 砂细度模数计算
    - 含泥量计算
  - 安全沙箱执行（防注入）
  - 文件：`backend/core/utils/formula.py`, `backend/apps/testing/formulas/`
  - 依赖：T-2.3.1

- [ ] **T-2.3.3** 结果判定引擎
  - JudgmentRule模型：判定规则（标准限值、设计值、等级对应表）
  - 自动合格/不合格判定
  - 混凝土强度等级评定（统计法/非统计法）
  - 不合格自动标记与预警推送
  - 文件：`backend/apps/testing/judgment.py`
  - 依赖：T-2.3.2

- [ ] **T-2.3.4** 检测结果数据模型与API
  - TestResult模型：原始值、修约值、判定结论、备注
  - 结果保存接口（触发自动计算+判定）
  - 结果查询与统计接口
  - 文件：`backend/apps/testing/models.py`（追加），`views.py`（追加）
  - 依赖：T-2.3.3

---

## 第三阶段：报告与设备（3周）

### 3.1 报告管理

- [ ] **T-3.1.1** 报告数据模型
  - Report模型：报告编号、关联委托/样品/结果、模板、状态（草稿/待审/待批/已发/作废）、CMA标识
  - ReportApproval模型：审批记录（审批人、角色、意见、时间、电子签名）
  - ReportDistribution模型：发放记录（接收人、方式、日期）
  - 文件：`backend/apps/reports/models.py`
  - 依赖：T-2.3.4

- [ ] **T-3.1.2** 报告模板引擎
  - Word模板设计（python-docx Jinja2模板）
  - PDF生成（WeasyPrint）
  - 预置模板：
    - 材料检测报告（通用）
    - 混凝土抗压强度检测报告
    - 钢筋力学性能检测报告
    - 桩基检测报告
  - CMA标识自动插入
  - 二维码防伪码嵌入
  - 文件：`backend/apps/reports/generator.py`, `backend/templates/reports/`
  - 依赖：T-3.1.1

- [ ] **T-3.1.3** 三级审批工作流
  - 工作流引擎：编制 -> 审核 -> 批准
  - 每级支持：通过/退回（含退回意见）
  - 审批权限校验（审核人须为报告审核人角色，批准人须为授权签字人）
  - 审批通知（系统消息）
  - 文件：`backend/apps/reports/workflow.py`
  - 依赖：T-3.1.1, T-1.2.2

- [ ] **T-3.1.4** 电子签名模块
  - 签名图片上传与管理
  - 签名插入报告（指定位置）
  - 签名验证（关联用户身份+密码二次确认）
  - 文件：`backend/apps/reports/signature.py`
  - 依赖：T-3.1.2

- [ ] **T-3.1.5** 报告管理前端页面
  - 报告列表（按状态Tab分类）
  - 报告预览（PDF内嵌预览）
  - 审批页面（意见填写 + 电子签名）
  - 报告发放登记
  - 报告台账查询与导出
  - 文件：`frontend/src/views/reports/`
  - 依赖：T-1.1.6, T-3.1.3

### 3.2 仪器设备管理

- [ ] **T-3.2.1** 设备数据模型
  - Equipment模型：名称、型号、出厂编号、管理编号、精度、量程、制造商、购入日期、分类（A/B/C）、状态（在用/停用/送检/报废）、存放位置
  - Calibration模型：检定/校准记录（证书号、有效期、校准机构、结论）
  - PeriodCheck模型：期间核查（计划日期、核查方法、核查结果）
  - Maintenance模型：维护保养记录
  - EquipUsageLog模型：使用记录（关联检测任务、使用人、开始/结束时间）
  - 文件：`backend/apps/equipment/models.py`
  - 依赖：T-1.1.4

- [ ] **T-3.2.2** 设备状态引擎
  - 校准到期自动计算（Celery定时任务）
  - 到期30天/7天提醒
  - 过期自动标记为"停用"
  - 期间核查计划自动生成
  - 维保计划提醒
  - 文件：`backend/apps/equipment/services.py`
  - 依赖：T-3.2.1

- [ ] **T-3.2.3** 设备管理API接口
  - 设备台账CRUD
  - 校准记录管理
  - 期间核查管理
  - 维保记录管理
  - 使用记录查询
  - 到期预警列表
  - 量值溯源树接口
  - 文件：`backend/apps/equipment/views.py`, `serializers.py`
  - 依赖：T-3.2.1, T-3.2.2

- [ ] **T-3.2.4** 设备管理前端页面
  - 设备台账列表（分类筛选、状态筛选）
  - 设备详情页（基本信息 + 校准历史 + 核查记录 + 维保记录 + 使用记录）
  - 设备新增/编辑表单
  - 校准到期日历视图
  - 量值溯源图（树形可视化）
  - 文件：`frontend/src/views/equipment/`
  - 依赖：T-1.1.6, T-3.2.3

---

## 第四阶段：质量体系与辅助（3周）

### 4.1 人员管理

- [ ] **T-4.1.1** 人员数据模型
  - Staff模型（扩展User）：工号、部门、职称、学历、专业、入职日期
  - Certificate模型：资质证书（证书类型、编号、发证机关、有效期）
  - Authorization模型：上岗授权（授权检测项目范围、授权日期、授权人）
  - Training模型：培训记录（培训内容、日期、考核结果）
  - CompetencyEval模型：能力评价记录
  - SignatureSample模型：签名样本
  - 文件：`backend/apps/staff/models.py`
  - 依赖：T-1.2.1

- [ ] **T-4.1.2** 人员管理API与前端
  - 人员档案CRUD
  - 资质证书管理（到期提醒）
  - 授权管理（授权/解除授权）
  - 培训记录管理
  - 能力评价管理
  - 前端页面：人员列表、详情、资质管理、授权管理
  - 文件：`backend/apps/staff/`, `frontend/src/views/staff/`
  - 依赖：T-4.1.1

### 4.2 环境监控

- [ ] **T-4.2.1** 环境监控数据模型与采集
  - MonitoringPoint模型：监控点位（养护室、试验室、标养室）
  - EnvRecord模型：环境记录（温度、湿度、采集时间、监控点位、状态）
  - 数据采集服务（HTTP/MQTT接口接收传感器数据）
  - 超标报警规则配置
  - 文件：`backend/apps/environment/models.py`, `services.py`
  - 依赖：T-1.1.4

- [ ] **T-4.2.2** 环境监控前端页面
  - 实时温湿度面板（数字大屏/仪表盘）
  - 历史曲线图（ECharts折线图）
  - 报警记录列表
  - 与检测记录自动关联
  - 文件：`frontend/src/views/environment/`
  - 依赖：T-4.2.1

### 4.3 标准规范管理

- [ ] **T-4.3.1** 标准库数据模型与管理
  - Standard模型：标准号、名称、发布日期、实施日期、废止日期、状态（现行/即将实施/已废止）、分类
  - MethodValidation模型：方法验证/确认记录
  - API接口：CRUD、有效性查询、变更通知
  - 前端页面：标准库列表、标准详情、方法验证记录
  - 文件：`backend/apps/standards/`, `frontend/src/views/standards/`
  - 依赖：T-1.1.4

### 4.4 质量管理体系

- [ ] **T-4.4.1** 内部审核模块
  - InternalAudit模型：审核计划、审核范围、审核组、审核日期
  - AuditFinding模型：审核发现（不符合项、观察项）
  - CorrectiveAction模型：纠正措施（原因分析、纠正方案、完成期限、验证结果）
  - API + 前端
  - 文件：`backend/apps/quality/`, `frontend/src/views/quality/audit/`
  - 依赖：T-1.1.4

- [ ] **T-4.4.2** 管理评审模块
  - ManagementReview模型：评审计划、输入材料清单、会议记录
  - ReviewDecision模型：评审决议、跟踪措施
  - API + 前端
  - 文件：`backend/apps/quality/`, `frontend/src/views/quality/review/`
  - 依赖：T-1.1.4

- [ ] **T-4.4.3** 不符合工作与投诉处理
  - NonConformity模型：不符合工作（来源、描述、影响评价、处置措施）
  - Complaint模型：投诉记录（投诉人、内容、调查结果、处理意见）
  - 闭环管理工作流
  - API + 前端
  - 文件：`backend/apps/quality/`, `frontend/src/views/quality/nonconformity/`
  - 依赖：T-1.1.4

- [ ] **T-4.4.4** 能力验证与质量监督
  - ProficiencyTest模型：能力验证/比对试验参加记录
  - QualitySupervision模型：质量监督计划与记录
  - API + 前端
  - 文件：`backend/apps/quality/`, `frontend/src/views/quality/proficiency/`
  - 依赖：T-1.1.4

### 4.5 耗材管理

- [ ] **T-4.5.1** 耗材管理模块
  - Consumable模型：名称、规格、厂家、有效期、库存量
  - ConsumableIn模型：入库记录
  - ConsumableOut模型：出库/领用记录
  - Supplier模型：供应商及评价
  - 库存预警（低于安全库存/即将过期）
  - API + 前端
  - 文件：`backend/apps/consumables/`, `frontend/src/views/consumables/`
  - 依赖：T-1.1.4

---

## 第五阶段：统计与优化（2周）

### 5.1 数据统计与分析

- [ ] **T-5.1.1** 统计分析API
  - 检测量统计（按时间/项目/类型维度）
  - 合格率统计与趋势分析
  - 混凝土强度发展曲线
  - 检测周期分析（从委托到出报告的平均周期）
  - 人员工作量统计
  - 设备利用率统计
  - 文件：`backend/apps/statistics/views.py`
  - 依赖：T-2.3.4, T-3.1.1

- [ ] **T-5.1.2** 数据看板前端
  - Dashboard首页（关键指标卡片 + 图表）
  - 检测量趋势图（ECharts柱状图/折线图）
  - 合格率饼图
  - 龄期日历热力图
  - 设备校准到期预警列表
  - 自定义报表导出（Excel/PDF）
  - 文件：`frontend/src/views/dashboard/`
  - 依赖：T-5.1.1

### 5.2 系统优化

- [ ] **T-5.2.1** 移动端适配
  - Element Plus响应式布局优化
  - 关键页面移动端适配：样品扫码登记、检测数据录入、审批操作
  - PWA离线支持（Service Worker缓存关键页面）
  - 文件：`frontend/src/`（改造）
  - 依赖：全部前端页面

- [ ] **T-5.2.2** 性能与安全优化
  - 数据库查询优化（索引、select_related/prefetch_related）
  - Redis缓存热点数据（字典表、权限树）
  - API限流
  - 敏感数据加密存储
  - HTTPS配置
  - 数据库自动备份脚本
  - 文件：各模块优化
  - 依赖：全部后端模块

- [ ] **T-5.2.3** 部署与文档
  - 生产环境Docker Compose配置
  - 数据库初始化脚本（字典数据、默认角色、管理员账号）
  - 用户操作手册
  - 系统部署文档
  - API接口文档（Swagger自动生成）
  - 文件：`docs/`
  - 依赖：全部模块
