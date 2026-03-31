# LIMIS 编码规则

## 硬性约束（必须遵守）

1. **单文件不超过 800 行**（含空行和注释）。超过必须拆分。
2. **单个函数/方法不超过 30 行**（纯代码行，不含空行和注释）。超过必须拆分为子函数。
3. **不写显而易见的注释**。只注释"为什么"，不注释"做了什么"。
4. **复杂计算公式必须注释对应的标准条文号**（如 `# GB/T 50081-2019 第5.1.2条`）。

## 后端规范（Django / Python）

- 所有业务 Model 继承 `core.models.BaseModel`
- View 层只做参数校验和响应返回，业务逻辑放 `services.py`
- API URL 路径：小写复数 kebab-case（`/api/v1/test-tasks/`）
- Model 类名：大驼峰单数
- Python 函数/变量：snake_case
- Serializer 命名：`{Model}Serializer`
- ViewSet 命名：`{Model}ViewSet`
- 统一响应格式：`{"code": 200, "message": "success", "data": {...}}`

## 前端规范（Vue 3 / TypeScript）

- 使用 `<script setup lang="ts">` 组合式 API
- 组件文件名：大驼峰（`SampleList.vue`）
- API 函数：`动词 + 名词`（`getSampleList`）
- Pinia Store：`use{Name}Store`
- Props/Emits 使用 TypeScript 类型声明

## 文件拆分策略

- `models.py` 超限 → 改为 `models/` 包
- `views.py` 超限 → 改为 `views/` 包
- `serializers.py` 超限 → 改为 `serializers/` 包
- `.vue` 文件超限 → 抽取子组件

## Git 工作流

- **默认开发分支**：`airport-site-lab-lims-741d`。在 Cursor 中的改动应提交并推送到该分支（勿默认推到 `main`，除非明确要做合并）。
- 推送示例：`git push -u origin airport-site-lab-lims-741d`

## 开发参考

开发前请阅读 `memory/` 目录下的文件：
- `01-project-overview.md` - 项目概览
- `02-tech-stack.md` - 技术栈
- `03-coding-conventions.md` - 完整编码规范
- `04-business-chain.md` - 业务链与状态机
- `05-database-design.md` - 数据库设计
- `06-standards-reference.md` - 检测标准参考
- `07-api-design.md` - API接口清单
- `08-directory-structure.md` - 目录结构
