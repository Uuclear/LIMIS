# Memory 文件索引

本目录包含 LIMIS 系统开发的所有参考记忆文件，供 AI 助手和开发者参考。

| 文件 | 内容 | 何时参考 |
|------|------|---------|
| `01-project-overview.md` | 项目背景、定位、合规要求、角色 | 任何开发任务开始前 |
| `02-tech-stack.md` | 技术栈决策、依赖列表 | 搭建环境、添加依赖时 |
| `03-coding-conventions.md` | 编码约束（800行/30行）、命名、分层、规范 | 编写任何代码时 |
| `04-business-chain.md` | 业务流程、状态机、业务规则、检测项目分类 | 开发业务模块时 |
| `05-database-design.md` | 实体关系、字段设计、索引策略、JSON Schema | 设计数据模型时 |
| `06-standards-reference.md` | 检测方法标准、修约规则、精度要求 | 开发计算引擎、原始记录时 |
| `07-api-design.md` | API接口清单、URL规范、响应格式 | 开发前后端接口时 |
| `08-directory-structure.md` | 完整目录树、文件拆分规则 | 创建新文件/模块时 |
| `09-csres-crawl-form-pitfalls.md` | 工标网爬取回填表单不完整/错位的原因与规避 | 改爬虫、标准表单、`request` 信封时 |

## 使用方式

在开发具体模块前，至少阅读以下文件：
1. 始终参考 `03-coding-conventions.md`（编码约束）
2. 根据模块参考 `04-business-chain.md`（业务规则）
3. 根据模块参考 `07-api-design.md`（接口定义）
4. 创建新文件时参考 `08-directory-structure.md`（目录规范）
