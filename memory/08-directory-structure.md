# 项目目录结构

## 完整目录树

```
/opt/limis/
├── docker-compose.yml              # Docker编排
├── docker-compose.dev.yml          # 开发环境覆盖
├── .env                            # 环境变量（不入库）
├── .env.example                    # 环境变量模板
├── .gitignore
├── README.md
├── memory/                         # 开发记忆文件（AI参考）
│   ├── 01-project-overview.md
│   ├── 02-tech-stack.md
│   ├── 03-coding-conventions.md
│   ├── 04-business-chain.md
│   ├── 05-database-design.md
│   ├── 06-standards-reference.md
│   ├── 07-api-design.md
│   └── 08-directory-structure.md
├── docs/                           # 项目文档
│   ├── PLAN.md                     # 系统规划文档
│   └── TODO.md                     # 任务拆分
│
├── backend/                        # ===== Django后端 =====
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── limis/                      # Django项目配置
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   ├── celery.py               # Celery配置
│   │   ├── urls.py                 # 根路由
│   │   └── settings/
│   │       ├── __init__.py
│   │       ├── base.py             # 基础配置
│   │       ├── dev.py              # 开发环境
│   │       └── prod.py             # 生产环境
│   │
│   ├── core/                       # 公共基础模块
│   │   ├── __init__.py
│   │   ├── models.py               # BaseModel基类
│   │   ├── serializers.py          # 基础序列化器
│   │   ├── views.py                # 基础视图类
│   │   ├── permissions.py          # 权限基类
│   │   ├── pagination.py           # 统一分页器
│   │   ├── exceptions.py           # 统一异常处理
│   │   ├── middleware.py           # 中间件（审计日志等）
│   │   ├── filters.py              # 通用过滤器
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── numbering.py        # 编号生成器
│   │       ├── rounding.py         # GB/T 8170 数值修约
│   │       ├── formula.py          # 计算公式引擎
│   │       ├── barcode.py          # 二维码/条码生成
│   │       └── export.py           # Excel/PDF导出
│   │
│   ├── apps/                       # ===== 业务模块 =====
│   │   ├── __init__.py
│   │   │
│   │   ├── system/                 # 系统管理
│   │   │   ├── models.py           # User, Role, Permission, AuditLog
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   │
│   │   ├── projects/               # 工程项目管理
│   │   │   ├── models.py           # Project, Organization, SubProject, Contract, Witness
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── filters.py
│   │   │   └── tests/
│   │   │
│   │   ├── commissions/            # 委托管理
│   │   │   ├── models.py           # Commission, CommissionItem, ContractReview
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   │
│   │   ├── samples/                # 样品管理
│   │   │   ├── models.py           # Sample, SampleGroup, SampleDisposal
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py         # 编号、二维码、盲样
│   │   │   └── tests/
│   │   │
│   │   ├── testing/                # 检测任务与数据
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task.py         # TestTask, TestCategory, TestProject
│   │   │   │   ├── record.py       # RecordTemplate, OriginalRecord, RecordRevision
│   │   │   │   ├── result.py       # TestResult, JudgmentRule
│   │   │   │   └── method.py       # TestMethod, TestParameter
│   │   │   ├── serializers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task.py
│   │   │   │   ├── record.py
│   │   │   │   └── result.py
│   │   │   ├── views/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task.py
│   │   │   │   ├── record.py
│   │   │   │   └── result.py
│   │   │   ├── urls.py
│   │   │   ├── services.py         # 任务分配、龄期计算
│   │   │   ├── judgment.py         # 结果判定引擎
│   │   │   ├── schemas/            # 原始记录JSON Schema
│   │   │   │   ├── concrete_compression.json
│   │   │   │   ├── rebar_tension.json
│   │   │   │   ├── cement_mortar.json
│   │   │   │   └── ...
│   │   │   ├── formulas/           # 计算公式定义
│   │   │   │   ├── __init__.py
│   │   │   │   ├── concrete.py
│   │   │   │   ├── rebar.py
│   │   │   │   ├── cement.py
│   │   │   │   └── aggregate.py
│   │   │   └── tests/
│   │   │
│   │   ├── reports/                # 报告管理
│   │   │   ├── models.py           # Report, ReportApproval, ReportDistribution
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── generator.py        # 报告生成引擎
│   │   │   ├── workflow.py         # 审批工作流
│   │   │   ├── signature.py        # 电子签名
│   │   │   └── tests/
│   │   │
│   │   ├── equipment/              # 仪器设备管理
│   │   │   ├── models.py           # Equipment, Calibration, PeriodCheck, Maintenance, EquipUsageLog
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py         # 到期提醒、状态管理
│   │   │   └── tests/
│   │   │
│   │   ├── staff/                  # 人员管理
│   │   │   ├── models.py           # Staff, Certificate, Authorization, Training, CompetencyEval
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── environment/            # 环境监控
│   │   │   ├── models.py           # MonitoringPoint, EnvRecord
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py         # 数据采集、报警
│   │   │   └── tests/
│   │   │
│   │   ├── standards/              # 标准管理
│   │   │   ├── models.py           # Standard, MethodValidation
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── quality/                # 质量管理体系
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audit.py        # InternalAudit, AuditFinding, CorrectiveAction
│   │   │   │   ├── review.py       # ManagementReview, ReviewDecision
│   │   │   │   ├── nonconformity.py # NonConformity, Complaint
│   │   │   │   └── proficiency.py  # ProficiencyTest, QualitySupervision
│   │   │   ├── serializers/
│   │   │   ├── views/
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── consumables/            # 耗材管理
│   │   │   ├── models.py           # Consumable, ConsumableIn, ConsumableOut, Supplier
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   └── statistics/             # 统计分析
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── services.py         # 统计计算逻辑
│   │       └── tests/
│   │
│   └── templates/                  # 报告Word/HTML模板
│       └── reports/
│           ├── concrete_strength.docx
│           ├── rebar_mechanics.docx
│           └── ...
│
├── frontend/                       # ===== Vue 3 前端 =====
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── api/                    # API接口（按模块分文件）
│       │   ├── auth.ts
│       │   ├── projects.ts
│       │   ├── commissions.ts
│       │   ├── samples.ts
│       │   ├── testing.ts
│       │   ├── reports.ts
│       │   ├── equipment.ts
│       │   ├── staff.ts
│       │   ├── environment.ts
│       │   ├── standards.ts
│       │   ├── quality.ts
│       │   ├── consumables.ts
│       │   └── statistics.ts
│       ├── types/                  # TypeScript类型定义
│       │   ├── project.ts
│       │   ├── commission.ts
│       │   ├── sample.ts
│       │   ├── testing.ts
│       │   ├── report.ts
│       │   ├── equipment.ts
│       │   └── ...
│       ├── stores/                 # Pinia状态管理
│       │   ├── user.ts
│       │   ├── permission.ts
│       │   └── dict.ts
│       ├── router/
│       │   ├── index.ts
│       │   └── modules/            # 路由模块（按业务分文件）
│       ├── views/                  # 页面组件
│       │   ├── login/
│       │   ├── dashboard/
│       │   ├── projects/
│       │   ├── commissions/
│       │   ├── samples/
│       │   ├── testing/
│       │   │   ├── tasks/
│       │   │   └── records/
│       │   ├── reports/
│       │   ├── equipment/
│       │   ├── staff/
│       │   ├── environment/
│       │   ├── standards/
│       │   ├── quality/
│       │   │   ├── audit/
│       │   │   ├── review/
│       │   │   └── nonconformity/
│       │   ├── consumables/
│       │   └── system/
│       ├── components/             # 公共组件
│       │   ├── Layout/             # 布局组件
│       │   ├── DynamicForm/        # 动态表单渲染
│       │   ├── SearchForm/         # 搜索表单
│       │   ├── DataTable/          # 数据表格封装
│       │   ├── ApprovalFlow/       # 审批流程组件
│       │   └── ...
│       ├── utils/
│       │   ├── request.ts          # Axios封装
│       │   ├── auth.ts             # Token管理
│       │   ├── permission.ts       # 权限工具
│       │   └── format.ts           # 格式化工具
│       └── assets/
│           ├── styles/
│           └── images/
│
└── nginx/                          # Nginx配置
    └── nginx.conf
```

## 文件拆分规则

当以下文件超过800行时的拆分方式：

| 原文件 | 拆分方式 |
|--------|---------|
| `models.py` | 改为 `models/` 包，按实体分文件，`__init__.py` 统一 import |
| `views.py` | 改为 `views/` 包，按资源分文件 |
| `serializers.py` | 改为 `serializers/` 包，按资源分文件 |
| `services.py` | 按业务主题拆分为多个 service 文件 |
| 单个 `.vue` 文件 | 抽取子组件到同级目录 |
| `urls.py` | 一般不会超限，无需拆分 |
