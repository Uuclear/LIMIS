# API概述

本文档描述LIMIS系统API的基础规范，包括认证方式、请求格式、响应格式、错误码定义、分页参数和接口版本等。

---

## 一、API基础信息

### 1.1 基础URL

| 环境 | URL | 说明 |
|------|-----|------|
| 开发环境 | `http://localhost:8000/api/v1/` | 本地开发 |
| 测试环境 | `http://test.example.com/api/v1/` | 测试服务器 |
| 生产环境 | `https://api.example.com/api/v1/` | 生产服务器 |

### 1.2 接口协议

- **协议**：HTTP/HTTPS
- **数据格式**：JSON
- **字符编码**：UTF-8
- **时间格式**：ISO 8601 (`YYYY-MM-DDTHH:mm:ssZ`)

### 1.3 接口版本

当前API版本：**v1**

版本控制方式：
- URL路径版本控制：`/api/v1/`
- 向后兼容原则：新增字段不影响现有客户端
- 版本升级通知：提前30天通知废弃接口

---

## 二、认证方式

### 2.1 JWT Token认证

系统使用JWT（JSON Web Token）进行身份认证。

#### 获取Token

**请求**：
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "password123"
}
```

**响应**：
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 3600
    }
}
```

#### 使用Token

在请求头中添加Authorization字段：

```http
GET /api/v1/system/users/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Token有效期

| Token类型 | 有效期 | 说明 |
|-----------|--------|------|
| access_token | 1小时 | 访问令牌，用于API请求 |
| refresh_token | 7天 | 刷新令牌，用于获取新的access_token |

#### 刷新Token

```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2.2 Token错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 0007 | Token无效 | 重新登录 |
| 0008 | Token过期 | 使用refresh_token刷新或重新登录 |
| 0009 | 账号被禁用 | 联系管理员 |

---

## 三、请求格式

### 3.1 请求头

| 请求头 | 必填 | 说明 |
|--------|------|------|
| Content-Type | 是 | `application/json` |
| Authorization | 是 | `Bearer {token}`（登录接口除外） |
| Accept | 否 | `application/json` |
| X-Request-ID | 否 | 请求唯一标识，用于追踪 |
| X-Client-Version | 否 | 客户端版本号 |

**示例**：
```http
GET /api/v1/system/users/ HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Client-Version: 1.0.0
```

### 3.2 请求方法

| 方法 | 说明 | 是否幂等 |
|------|------|----------|
| GET | 获取资源 | 是 |
| POST | 创建资源 | 否 |
| PUT | 全量更新资源 | 是 |
| PATCH | 部分更新资源 | 是 |
| DELETE | 删除资源 | 是 |

### 3.3 请求参数

#### Query参数

用于GET请求的筛选、排序和分页：

```http
GET /api/v1/system/users/?page=1&page_size=20&status=active&ordering=-created_at
```

#### Path参数

用于指定资源ID：

```http
GET /api/v1/system/users/1/
```

#### Body参数

用于POST、PUT、PATCH请求的数据提交：

```http
POST /api/v1/system/users/
Content-Type: application/json

{
    "username": "zhangsan",
    "name": "张三",
    "email": "zhangsan@example.com"
}
```

### 3.4 参数命名规范

- 使用**snake_case**命名（小写字母+下划线）
- 示例：`user_name`、`created_at`、`department_id`

---

## 四、响应格式

### 4.1 标准响应结构

所有API响应均采用统一的JSON格式：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        // 响应数据
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 业务状态码 |
| message | string | 响应消息 |
| data | object/array/null | 响应数据 |
| timestamp | string | 响应时间戳 |

### 4.2 成功响应

#### 单条数据响应

```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "username": "admin",
        "name": "系统管理员",
        "email": "admin@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 列表数据响应

```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "username": "admin",
                "name": "系统管理员"
            },
            {
                "id": 2,
                "username": "zhangsan",
                "name": "张三"
            }
        ],
        "total": 50,
        "page": 1,
        "page_size": 20,
        "total_pages": 3
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 创建成功响应

```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 10,
        "username": "lisi",
        "name": "李四"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 删除成功响应

```json
{
    "code": 200,
    "message": "删除成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4.3 错误响应

#### 参数错误

```json
{
    "code": 0002,
    "message": "参数错误",
    "data": {
        "errors": [
            {
                "field": "email",
                "message": "邮箱格式不正确"
            },
            {
                "field": "phone",
                "message": "手机号格式不正确"
            }
        ]
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 权限错误

```json
{
    "code": 0006,
    "message": "权限不足",
    "data": {
        "required_permission": "user.delete"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 业务错误

```json
{
    "code": 1001,
    "message": "用户名已存在",
    "data": {
        "field": "username",
        "value": "admin"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 五、错误码定义

### 5.1 通用错误码（0xxx）

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 0000 | 成功 | 200 |
| 0001 | 系统异常 | 500 |
| 0002 | 参数错误 | 400 |
| 0003 | 数据不存在 | 404 |
| 0004 | 数据已存在 | 409 |
| 0005 | 操作失败 | 400 |
| 0006 | 权限不足 | 403 |
| 0007 | Token无效 | 401 |
| 0008 | Token过期 | 401 |
| 0009 | 账号被禁用 | 403 |
| 0010 | 验证码错误 | 400 |
| 0011 | 请求频率超限 | 429 |
| 0012 | 服务暂时不可用 | 503 |

### 5.2 用户模块错误码（1xxx）

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 1001 | 用户名已存在 | 409 |
| 1002 | 邮箱已存在 | 409 |
| 1003 | 用户不存在 | 404 |
| 1004 | 密码错误 | 400 |
| 1005 | 用户已禁用 | 403 |
| 1006 | 用户已删除 | 410 |
| 1007 | 原密码错误 | 400 |
| 1008 | 新密码格式错误 | 400 |
| 1009 | 手机号已存在 | 409 |
| 1010 | 用户未激活 | 403 |

### 5.3 委托模块错误码（2xxx）

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 2001 | 委托不存在 | 404 |
| 2002 | 委托状态不允许此操作 | 400 |
| 2003 | 委托已提交 | 409 |
| 2004 | 委托已受理 | 409 |
| 2005 | 委托已取消 | 410 |
| 2006 | 委托编号已存在 | 409 |
| 2007 | 检测项目不能为空 | 400 |
| 2008 | 样品信息不完整 | 400 |

### 5.4 样品模块错误码（3xxx）

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 3001 | 样品不存在 | 404 |
| 3002 | 样品状态不允许此操作 | 400 |
| 3003 | 样品编号已存在 | 409 |
| 3004 | 样品已接收 | 409 |
| 3005 | 样品已流转 | 409 |
| 3006 | 样品已处置 | 410 |
| 3007 | 样品数量不足 | 400 |
| 3008 | 样品位置冲突 | 409 |

### 5.5 检测任务模块错误码（4xxx）

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 4001 | 任务不存在 | 404 |
| 4002 | 任务状态不允许此操作 | 400 |
| 4003 | 任务已分配 | 409 |
| 4004 | 任务已开始 | 409 |
| 4005 | 任务已完成 | 409 |
| 4006 | 任务已取消 | 410 |
| 4007 | 检测人员不可用 | 400 |
| 4008 | 设备不可用 | 400 |

### 5.6 报告模块错误码（5xxx）

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 5001 | 报告不存在 | 404 |
| 5002 | 报告状态不允许此操作 | 400 |
| 5003 | 报告已提交 | 409 |
| 5004 | 报告已审核 | 409 |
| 5005 | 报告已签发 | 409 |
| 5006 | 报告已作废 | 410 |
| 5007 | 报告编号已存在 | 409 |
| 5008 | 报告模板不存在 | 404 |

### 5.7 文件模块错误码（6xxx）

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 6001 | 文件不存在 | 404 |
| 6002 | 文件大小超限 | 400 |
| 6003 | 文件格式不支持 | 400 |
| 6004 | 文件上传失败 | 500 |
| 6005 | 文件删除失败 | 500 |
| 6006 | 文件名不合法 | 400 |
| 6007 | 文件已删除 | 410 |

---

## 六、分页参数

### 6.1 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码，从1开始 |
| page_size | integer | 20 | 每页数量，最大100 |

**示例**：
```http
GET /api/v1/system/users/?page=2&page_size=50
```

### 6.2 响应格式

```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [...],
        "total": 150,
        "page": 2,
        "page_size": 50,
        "total_pages": 3
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 数据列表 |
| total | integer | 总记录数 |
| page | integer | 当前页码 |
| page_size | integer | 每页数量 |
| total_pages | integer | 总页数 |

### 6.3 分页限制

- 单页最大记录数：100条
- 单次查询最大记录数：10000条
- 深度分页限制：页码不超过1000页

---

## 七、排序参数

### 7.1 请求参数

使用`ordering`参数进行排序：

| 参数 | 说明 |
|------|------|
| ordering=created_at | 按创建时间升序 |
| ordering=-created_at | 按创建时间降序 |
| ordering=name,-created_at | 多字段排序（先按name升序，再按created_at降序） |

**示例**：
```http
GET /api/v1/system/users/?ordering=-created_at
GET /api/v1/system/users/?ordering=name,-created_at
```

### 7.2 支持排序的字段

每个接口的排序字段可能不同，具体请参考各接口文档。常见排序字段：

| 字段 | 说明 |
|------|------|
| id | ID |
| created_at | 创建时间 |
| updated_at | 更新时间 |
| name | 名称 |
| code | 编码 |
| status | 状态 |

---

## 八、筛选参数

### 8.1 基本筛选

```http
GET /api/v1/system/users/?status=active&department_id=1
```

### 8.2 模糊筛选

使用`search`参数进行模糊搜索：

```http
GET /api/v1/system/users/?search=张三
```

### 8.3 范围筛选

日期和数字范围筛选：

```http
GET /api/v1/commissions/?created_at__gte=2024-01-01&created_at__lte=2024-01-31
GET /api/v1/samples/?quantity__gt=10&quantity__lt=100
```

| 筛选器 | 说明 |
|--------|------|
| __gt | 大于 |
| __gte | 大于等于 |
| __lt | 小于 |
| __lte | 小于等于 |
| __in | 包含（逗号分隔） |
| __ne | 不等于 |

### 8.4 多值筛选

```http
GET /api/v1/system/users/?status__in=active,pending
GET /api/v1/commissions/?id__in=1,2,3,4,5
```

---

## 九、接口版本管理

### 9.1 版本规则

采用语义化版本控制（Semantic Versioning）：

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR: 主版本号，不兼容的API变更
MINOR: 次版本号，向后兼容的功能新增
PATCH: 补丁版本号，向后兼容的问题修复
```

### 9.2 版本生命周期

| 阶段 | 说明 | 时长 |
|------|------|------|
| Current | 当前版本，完全支持 | - |
| Deprecated | 已废弃，仍可用但建议迁移 | 6个月 |
| Retired | 已下线，不再可用 | - |

### 9.3 版本迁移

当API版本升级时，系统会：
1. 提前30天发布迁移公告
2. 提供新旧版本对照文档
3. 在过渡期同时支持新旧版本
4. 废弃接口返回警告信息

**废弃接口响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {...},
    "timestamp": "2024-01-01T12:00:00Z",
    "deprecation": {
        "deprecated": true,
        "message": "此接口已废弃，请使用 /api/v2/system/users/",
        "sunset": "2024-06-01T00:00:00Z"
    }
}
```

---

## 十、请求限流

### 10.1 限流规则

| 用户类型 | 限流规则 | 说明 |
|----------|----------|------|
| 匿名用户 | 60次/分钟 | 未登录用户 |
| 普通用户 | 300次/分钟 | 已登录用户 |
| VIP用户 | 1000次/分钟 | 特殊权限用户 |

### 10.2 限流响应

当请求超过限流阈值时，返回429错误：

```json
{
    "code": 0011,
    "message": "请求频率超限，请稍后再试",
    "data": {
        "retry_after": 60
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 10.3 响应头

限流信息会在响应头中返回：

```http
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 299
X-RateLimit-Reset: 1704110400
```

---

## 十一、通用字段说明

### 11.1 时间字段

| 字段 | 类型 | 说明 |
|------|------|------|
| created_at | string | 创建时间，ISO 8601格式 |
| updated_at | string | 更新时间，ISO 8601格式 |
| deleted_at | string | 删除时间，ISO 8601格式（软删除） |

**示例**：
```json
{
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-02T15:30:00Z"
}
```

### 11.2 状态字段

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 状态标识 |
| status_display | string | 状态显示名称 |

**常见状态值**：

| 状态 | 说明 |
|------|------|
| active | 启用/正常 |
| inactive | 未激活 |
| disabled | 禁用 |
| deleted | 已删除 |
| pending | 待处理 |
| processing | 处理中 |
| completed | 已完成 |
| cancelled | 已取消 |

### 11.3 关联字段

关联对象通常返回简化信息：

```json
{
    "id": 1,
    "name": "张三",
    "department": {
        "id": 1,
        "name": "信息中心"
    },
    "roles": [
        {
            "id": 1,
            "name": "admin",
            "display_name": "系统管理员"
        }
    ]
}
```

---

## 十二、API调用示例

### 12.1 cURL示例

```bash
# 登录获取Token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# 获取用户列表
curl -X GET http://localhost:8000/api/v1/system/users/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 创建用户
curl -X POST http://localhost:8000/api/v1/system/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{"username": "zhangsan", "name": "张三", "email": "zhangsan@example.com"}'

# 更新用户
curl -X PUT http://localhost:8000/api/v1/system/users/10/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{"name": "张三更新"}'

# 删除用户
curl -X DELETE http://localhost:8000/api/v1/system/users/10/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 12.2 JavaScript示例

```javascript
// 使用fetch API
const API_BASE = 'http://localhost:8000/api/v1';

// 登录
async function login(username, password) {
    const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (data.code === 200) {
        localStorage.setItem('access_token', data.data.access_token);
        localStorage.setItem('refresh_token', data.data.refresh_token);
    }
    return data;
}

// 获取用户列表
async function getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${API_BASE}/system/users/?${queryString}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    return response.json();
}

// 创建用户
async function createUser(userData) {
    const response = await fetch(`${API_BASE}/system/users/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(userData)
    });
    return response.json();
}
```

### 12.3 Python示例

```python
import requests

API_BASE = 'http://localhost:8000/api/v1'

class LIMISClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
    
    def login(self, username, password):
        """登录获取Token"""
        response = requests.post(
            f'{API_BASE}/auth/login/',
            json={'username': username, 'password': password}
        )
        data = response.json()
        if data['code'] == 200:
            self.access_token = data['data']['access_token']
            self.refresh_token = data['data']['refresh_token']
        return data
    
    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_users(self, **params):
        """获取用户列表"""
        response = requests.get(
            f'{API_BASE}/system/users/',
            headers=self.get_headers(),
            params=params
        )
        return response.json()
    
    def create_user(self, user_data):
        """创建用户"""
        response = requests.post(
            f'{API_BASE}/system/users/',
            headers=self.get_headers(),
            json=user_data
        )
        return response.json()
    
    def update_user(self, user_id, user_data):
        """更新用户"""
        response = requests.put(
            f'{API_BASE}/system/users/{user_id}/',
            headers=self.get_headers(),
            json=user_data
        )
        return response.json()
    
    def delete_user(self, user_id):
        """删除用户"""
        response = requests.delete(
            f'{API_BASE}/system/users/{user_id}/',
            headers=self.get_headers()
        )
        return response.json()

# 使用示例
client = LIMISClient()
client.login('admin', 'password123')

# 获取用户列表
users = client.get_users(page=1, page_size=20, status='active')

# 创建用户
new_user = client.create_user({
    'username': 'zhangsan',
    'name': '张三',
    'email': 'zhangsan@example.com'
})

# 更新用户
client.update_user(new_user['data']['id'], {'name': '张三更新'})

# 删除用户
client.delete_user(new_user['data']['id'])
```

---

## 十三、最佳实践

### 13.1 安全建议

1. **Token存储**：不要将Token存储在localStorage，建议使用httpOnly cookie
2. **HTTPS**：生产环境必须使用HTTPS
3. **Token刷新**：在Token过期前主动刷新
4. **敏感数据**：不要在URL中传递敏感数据

### 13.2 性能优化

1. **分页查询**：大数据量使用分页，避免一次性获取
2. **字段筛选**：只获取需要的字段
3. **缓存利用**：合理使用客户端缓存
4. **批量操作**：使用批量接口减少请求次数

### 13.3 错误处理

1. **统一处理**：封装统一的错误处理逻辑
2. **重试机制**：对临时性错误实现重试
3. **日志记录**：记录错误信息便于排查
4. **用户提示**：友好的错误提示信息

---

*文档版本: v1.0.0*
*最后更新: 2024年*