# 编码约束与开发规范

## 硬性约束

### 文件大小限制
- **单文件不超过 800 行**（含空行和注释）
- 超过 800 行时必须拆分为多个文件

### 函数大小限制
- **单个函数/方法不超过 30 行**（不含空行和注释的纯代码行）
- 超过 30 行时必须拆分为子函数

### 拆分策略
- Model 文件过长时：按功能分拆到同目录 `models/` 包中（`__init__.py` 统一导出）
- View 文件过长时：按资源类型分拆到 `views/` 包中
- Serializer 文件过长时：同理分拆到 `serializers/` 包中
- 前端页面过长时：拆分为子组件放入同名目录

## 后端规范（Django / Python）

### 项目结构约定
- 每个 Django App 标准文件结构：
  ```
  apps/模块名/
    __init__.py
    models.py          # 数据模型（或 models/ 包）
    serializers.py     # 序列化器（或 serializers/ 包）
    views.py           # 视图（或 views/ 包）
    urls.py            # 路由
    services.py        # 业务逻辑层（复杂逻辑不要写在 View 中）
    filters.py         # 查询过滤器
    signals.py         # 信号处理
    admin.py           # Admin配置
    tests/             # 测试目录
      __init__.py
      test_models.py
      test_views.py
      test_services.py
  ```

### 命名规范
- Model 类名：大驼峰单数（`Sample`, `TestTask`, `Equipment`）
- Serializer 类名：`{Model}Serializer`
- ViewSet 类名：`{Model}ViewSet`
- URL路径：小写复数 kebab-case（`/api/v1/test-tasks/`）
- Python变量/函数：snake_case
- 常量：UPPER_SNAKE_CASE

### 代码分层
```
View（接收请求、参数校验、返回响应）
  ↓
Service（业务逻辑、事务控制）
  ↓
Model（数据访问、查询）
```
- View 只做参数接收和响应返回，不写业务逻辑
- 复杂业务逻辑统一放在 services.py
- Model 中只放数据定义和简单查询方法

### 数据模型基类
所有业务 Model 统一继承 `BaseModel`：
```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, ...)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
```

### API 版本
- URL 前缀：`/api/v1/`
- 统一响应格式：
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 异常处理
- 使用统一异常处理器（`core/exceptions.py`）
- 业务异常抛出自定义异常类，由处理器统一捕获返回

## 前端规范（Vue 3 / TypeScript）

### 文件结构约定
- 页面组件放 `views/模块名/` 目录
- 公共组件放 `components/`
- API 接口按模块分文件 `api/模块名.ts`
- TypeScript 类型定义 `types/模块名.ts`

### 命名规范
- 组件文件名：大驼峰（`SampleList.vue`）
- 组合式函数：`use` 前缀（`useSampleList.ts`）
- API 函数：`动词 + 名词`（`getSampleList`, `createCommission`）
- Pinia Store：`use{Name}Store`
- CSS 类名：BEM 或 Element Plus 风格

### 组件规范
- 使用 `<script setup lang="ts">` 组合式API
- Props 使用 `defineProps<T>()` 类型声明
- Emits 使用 `defineEmits<T>()`
- 单个 `.vue` 文件不超过 800 行，超过则拆分子组件

### 状态管理
- 全局状态用 Pinia（用户信息、权限、字典数据）
- 页面级状态用 composable（`use*.ts`）
- 组件级状态用 `ref`/`reactive`

## 通用规范

### Git 提交
- feat: 新功能
- fix: 修复缺陷
- refactor: 重构
- docs: 文档
- style: 格式
- test: 测试
- chore: 构建/工具

### 注释原则
- 不写显而易见的注释
- 只注释"为什么"，不注释"做了什么"
- 复杂计算公式必须注释对应的标准条文号
- API 接口必须写 docstring

### 测试要求
- Model 层：单元测试
- Service 层：单元测试 + 集成测试
- API 层：接口测试
- 计算引擎：必须100%覆盖（修约、公式、判定）
