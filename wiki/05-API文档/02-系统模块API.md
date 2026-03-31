# 系统模块API

本文档描述LIMIS系统模块的API接口，包括用户管理、角色管理、权限管理、登录登出、审计日志和通知等功能。

---

## 一、认证API

### 1.1 用户登录

**端点**：`POST /api/v1/auth/login/`

**描述**：用户登录系统，获取访问令牌

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| captcha | string | 否 | 验证码（需要时） |
| captcha_key | string | 否 | 验证码key |

**请求示例**：
```json
{
    "username": "admin",
    "password": "password123",
    "captcha": "1234",
    "captcha_key": "abc123"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "id": 1,
            "username": "admin",
            "name": "系统管理员",
            "email": "admin@example.com",
            "phone": "13800138000",
            "avatar": "/media/avatars/admin.jpg",
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
            ],
            "permissions": [
                "user.view",
                "user.create",
                "user.update",
                "user.delete"
            ]
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1001 | 用户名不存在 | 检查用户名是否正确 |
| 1004 | 密码错误 | 检查密码是否正确 |
| 1005 | 用户已禁用 | 联系管理员启用账号 |
| 0010 | 验证码错误 | 重新获取验证码 |

---

### 1.2 用户登出

**端点**：`POST /api/v1/auth/logout/`

**描述**：用户登出系统，注销令牌

**请求头**：
```
Authorization: Bearer {access_token}
```

**请求参数**：无

**响应示例**：
```json
{
    "code": 200,
    "message": "登出成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 0007 | Token无效 | 重新登录 |
| 0008 | Token过期 | 使用refresh_token刷新或重新登录 |

---

### 1.3 刷新Token

**端点**：`POST /api/v1/auth/refresh/`

**描述**：使用refresh_token获取新的access_token

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | 是 | 刷新令牌 |

**请求示例**：
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "Token刷新成功",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 3600
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 0008 | refresh_token已过期 | 重新登录 |

---

### 1.4 获取当前用户信息

**端点**：`GET /api/v1/auth/me/`

**描述**：获取当前登录用户的详细信息

**请求参数**：无

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "username": "admin",
        "name": "系统管理员",
        "email": "admin@example.com",
        "phone": "13800138000",
        "avatar": "/media/avatars/admin.jpg",
        "status": "active",
        "department": {
            "id": 1,
            "name": "信息中心",
            "code": "INFO"
        },
        "roles": [
            {
                "id": 1,
                "name": "admin",
                "display_name": "系统管理员"
            }
        ],
        "permissions": [
            "user.view",
            "user.create",
            "user.update",
            "user.delete",
            "role.view",
            "role.create"
        ],
        "last_login": "2024-01-01T10:00:00Z",
        "created_at": "2023-01-01T00:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.5 修改密码

**端点**：`POST /api/v1/auth/change-password/`

**描述**：修改当前用户密码

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码 |
| confirm_password | string | 是 | 确认新密码 |

**请求示例**：
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword456",
    "confirm_password": "newpassword456"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "密码修改成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1007 | 原密码错误 | 确认原密码是否正确 |
| 1008 | 新密码格式错误 | 密码需8-20位，包含字母和数字 |
| 0002 | 两次密码不一致 | 确认新密码输入一致 |

---

## 二、用户管理API

### 2.1 获取用户列表

**端点**：`GET /api/v1/system/users/`

**描述**：获取系统用户列表，支持分页、筛选和排序

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |
| search | string | 否 | 搜索关键词（用户名/姓名/邮箱） |
| status | string | 否 | 状态筛选：active/inactive/disabled |
| department_id | integer | 否 | 部门ID筛选 |
| role_id | integer | 否 | 角色ID筛选 |
| ordering | string | 否 | 排序字段 |

**请求示例**：
```http
GET /api/v1/system/users/?page=1&page_size=20&status=active&ordering=-created_at
```

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "username": "admin",
                "name": "系统管理员",
                "email": "admin@example.com",
                "phone": "13800138000",
                "status": "active",
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
                ],
                "last_login": "2024-01-01T10:00:00Z",
                "created_at": "2023-01-01T00:00:00Z"
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

---

### 2.2 获取用户详情

**端点**：`GET /api/v1/system/users/{id}/`

**描述**：获取指定用户的详细信息

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 用户ID |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "username": "admin",
        "name": "系统管理员",
        "email": "admin@example.com",
        "phone": "13800138000",
        "avatar": "/media/avatars/admin.jpg",
        "status": "active",
        "gender": "male",
        "birthday": "1990-01-01",
        "address": "北京市朝阳区xxx",
        "department": {
            "id": 1,
            "name": "信息中心",
            "code": "INFO"
        },
        "roles": [
            {
                "id": 1,
                "name": "admin",
                "display_name": "系统管理员"
            }
        ],
        "permissions": [
            "user.view",
            "user.create",
            "user.update",
            "user.delete"
        ],
        "last_login": "2024-01-01T10:00:00Z",
        "login_count": 100,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.3 创建用户

**端点**：`POST /api/v1/system/users/`

**描述**：创建新用户

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，4-20位字母数字 |
| password | string | 是 | 密码，8-20位 |
| name | string | 是 | 姓名 |
| email | string | 是 | 邮箱地址 |
| phone | string | 否 | 手机号 |
| department_id | integer | 否 | 部门ID |
| role_ids | array | 否 | 角色ID列表 |
| status | string | 否 | 状态，默认active |
| gender | string | 否 | 性别：male/female |
| birthday | string | 否 | 生日，格式YYYY-MM-DD |
| address | string | 否 | 地址 |

**请求示例**：
```json
{
    "username": "zhangsan",
    "password": "password123",
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13900139000",
    "department_id": 2,
    "role_ids": [2, 3],
    "status": "active",
    "gender": "male"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 10,
        "username": "zhangsan",
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13900139000",
        "status": "active",
        "department": {
            "id": 2,
            "name": "检测部"
        },
        "roles": [
            {
                "id": 2,
                "name": "tester",
                "display_name": "检测员"
            },
            {
                "id": 3,
                "name": "reviewer",
                "display_name": "审核员"
            }
        ],
        "created_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1001 | 用户名已存在 | 更换用户名 |
| 1002 | 邮箱已存在 | 更换邮箱 |
| 0002 | 参数格式错误 | 检查参数格式 |

---

### 2.4 更新用户

**端点**：`PUT /api/v1/system/users/{id}/`

**描述**：全量更新用户信息

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 用户ID |

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 姓名 |
| email | string | 是 | 邮箱地址 |
| phone | string | 否 | 手机号 |
| department_id | integer | 否 | 部门ID |
| role_ids | array | 否 | 角色ID列表 |
| status | string | 否 | 状态 |
| gender | string | 否 | 性别 |
| birthday | string | 否 | 生日 |
| address | string | 否 | 地址 |

**请求示例**：
```json
{
    "name": "张三更新",
    "email": "zhangsan_new@example.com",
    "phone": "13900139001",
    "department_id": 3,
    "role_ids": [2],
    "status": "active"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "更新成功",
    "data": {
        "id": 10,
        "username": "zhangsan",
        "name": "张三更新",
        "email": "zhangsan_new@example.com",
        "phone": "13900139001",
        "status": "active",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.5 部分更新用户

**端点**：`PATCH /api/v1/system/users/{id}/`

**描述**：部分更新用户信息

**请求示例**：
```json
{
    "name": "张三更新",
    "status": "inactive"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "更新成功",
    "data": {
        "id": 10,
        "username": "zhangsan",
        "name": "张三更新",
        "status": "inactive",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.6 删除用户

**端点**：`DELETE /api/v1/system/users/{id}/`

**描述**：删除指定用户（软删除）

**响应示例**：
```json
{
    "code": 200,
    "message": "删除成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1003 | 用户不存在 | 检查用户ID |
| 0006 | 权限不足 | 联系管理员 |
| 0005 | 不能删除自己 | 使用其他账号操作 |

---

### 2.7 重置用户密码

**端点**：`POST /api/v1/system/users/{id}/reset-password/`

**描述**：管理员重置用户密码

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| new_password | string | 是 | 新密码 |

**请求示例**：
```json
{
    "new_password": "newpassword123"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "密码重置成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.8 启用/禁用用户

**端点**：`POST /api/v1/system/users/{id}/toggle-status/`

**描述**：切换用户启用/禁用状态

**响应示例**：
```json
{
    "code": 200,
    "message": "用户状态已更新",
    "data": {
        "id": 10,
        "status": "disabled"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 三、角色管理API

### 3.1 获取角色列表

**端点**：`GET /api/v1/system/roles/`

**描述**：获取系统角色列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| search | string | 否 | 搜索关键词 |
| is_system | boolean | 否 | 是否系统角色 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "name": "admin",
                "display_name": "系统管理员",
                "description": "系统管理员，拥有所有权限",
                "is_system": true,
                "status": "active",
                "user_count": 2,
                "permissions_count": 50,
                "created_at": "2023-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "name": "tester",
                "display_name": "检测员",
                "description": "检测人员角色",
                "is_system": false,
                "status": "active",
                "user_count": 10,
                "permissions_count": 15,
                "created_at": "2023-01-01T00:00:00Z"
            }
        ],
        "total": 5,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.2 获取角色详情

**端点**：`GET /api/v1/system/roles/{id}/`

**描述**：获取角色详细信息，包括权限列表

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 2,
        "name": "tester",
        "display_name": "检测员",
        "description": "检测人员角色",
        "is_system": false,
        "status": "active",
        "permissions": [
            {
                "id": 10,
                "code": "commission.view",
                "name": "查看委托",
                "module": "委托管理"
            },
            {
                "id": 11,
                "code": "commission.create",
                "name": "创建委托",
                "module": "委托管理"
            }
        ],
        "users": [
            {
                "id": 5,
                "username": "tester1",
                "name": "检测员1"
            }
        ],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.3 创建角色

**端点**：`POST /api/v1/system/roles/`

**描述**：创建新角色

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 角色标识，唯一 |
| display_name | string | 是 | 角色显示名称 |
| description | string | 否 | 角色描述 |
| permission_ids | array | 否 | 权限ID列表 |
| status | string | 否 | 状态，默认active |

**请求示例**：
```json
{
    "name": "sample_manager",
    "display_name": "样品管理员",
    "description": "负责样品管理的角色",
    "permission_ids": [20, 21, 22, 23],
    "status": "active"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 10,
        "name": "sample_manager",
        "display_name": "样品管理员",
        "description": "负责样品管理的角色",
        "status": "active",
        "permissions_count": 4,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.4 更新角色

**端点**：`PUT /api/v1/system/roles/{id}/`

**描述**：更新角色信息

**请求示例**：
```json
{
    "display_name": "样品管理员（更新）",
    "description": "负责样品管理的角色（已更新）",
    "permission_ids": [20, 21, 22, 23, 24],
    "status": "active"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "更新成功",
    "data": {
        "id": 10,
        "name": "sample_manager",
        "display_name": "样品管理员（更新）",
        "description": "负责样品管理的角色（已更新）",
        "permissions_count": 5,
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.5 删除角色

**端点**：`DELETE /api/v1/system/roles/{id}/`

**描述**：删除角色

**响应示例**：
```json
{
    "code": 200,
    "message": "删除成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 0005 | 系统角色不能删除 | 系统角色不可删除 |
| 0005 | 角色下有用户 | 先移除用户再删除 |

---

### 3.6 获取角色权限

**端点**：`GET /api/v1/system/roles/{id}/permissions/`

**描述**：获取角色的权限列表

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": [
        {
            "id": 10,
            "code": "commission.view",
            "name": "查看委托",
            "module": "委托管理",
            "category": "业务权限"
        },
        {
            "id": 11,
            "code": "commission.create",
            "name": "创建委托",
            "module": "委托管理",
            "category": "业务权限"
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.7 更新角色权限

**端点**：`PUT /api/v1/system/roles/{id}/permissions/`

**描述**：更新角色的权限

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| permission_ids | array | 是 | 权限ID列表 |

**请求示例**：
```json
{
    "permission_ids": [10, 11, 12, 13, 14]
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "权限更新成功",
    "data": {
        "permissions_count": 5
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 四、权限管理API

### 4.1 获取权限列表

**端点**：`GET /api/v1/system/permissions/`

**描述**：获取系统所有权限列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| module | string | 否 | 模块筛选 |
| category | string | 否 | 分类筛选 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": [
        {
            "id": 1,
            "code": "user.view",
            "name": "查看用户",
            "module": "系统管理",
            "category": "用户权限",
            "description": "查看用户列表和详情"
        },
        {
            "id": 2,
            "code": "user.create",
            "name": "创建用户",
            "module": "系统管理",
            "category": "用户权限",
            "description": "创建新用户"
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 4.2 获取权限树

**端点**：`GET /api/v1/system/permissions/tree/`

**描述**：获取权限树形结构，用于权限配置

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": [
        {
            "module": "系统管理",
            "categories": [
                {
                    "category": "用户权限",
                    "permissions": [
                        {
                            "id": 1,
                            "code": "user.view",
                            "name": "查看用户"
                        },
                        {
                            "id": 2,
                            "code": "user.create",
                            "name": "创建用户"
                        },
                        {
                            "id": 3,
                            "code": "user.update",
                            "name": "更新用户"
                        },
                        {
                            "id": 4,
                            "code": "user.delete",
                            "name": "删除用户"
                        }
                    ]
                },
                {
                    "category": "角色权限",
                    "permissions": [
                        {
                            "id": 5,
                            "code": "role.view",
                            "name": "查看角色"
                        },
                        {
                            "id": 6,
                            "code": "role.create",
                            "name": "创建角色"
                        }
                    ]
                }
            ]
        },
        {
            "module": "委托管理",
            "categories": [
                {
                    "category": "业务权限",
                    "permissions": [
                        {
                            "id": 10,
                            "code": "commission.view",
                            "name": "查看委托"
                        },
                        {
                            "id": 11,
                            "code": "commission.create",
                            "name": "创建委托"
                        }
                    ]
                }
            ]
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 4.3 获取用户权限

**端点**：`GET /api/v1/system/users/{id}/permissions/`

**描述**：获取指定用户的所有权限

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "user_id": 10,
        "permissions": [
            "user.view",
            "user.create",
            "commission.view",
            "commission.create"
        ],
        "roles": [
            {
                "id": 2,
                "name": "tester",
                "display_name": "检测员"
            }
        ]
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 五、审计日志API

### 5.1 获取审计日志列表

**端点**：`GET /api/v1/system/audit-logs/`

**描述**：获取系统审计日志列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| user_id | integer | 否 | 用户ID筛选 |
| module | string | 否 | 模块筛选 |
| action | string | 否 | 操作类型：create/update/delete/login/logout |
| start_time | string | 否 | 开始时间，格式YYYY-MM-DD HH:mm:ss |
| end_time | string | 否 | 结束时间 |
| ip_address | string | 否 | IP地址筛选 |
| search | string | 否 | 搜索关键词 |

**请求示例**：
```http
GET /api/v1/system/audit-logs/?page=1&page_size=20&module=用户管理&action=create&start_time=2024-01-01&end_time=2024-01-31
```

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1001,
                "user": {
                    "id": 1,
                    "username": "admin",
                    "name": "系统管理员"
                },
                "module": "用户管理",
                "action": "create",
                "description": "创建用户：zhangsan",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "request_method": "POST",
                "request_url": "/api/v1/system/users/",
                "request_data": {
                    "username": "zhangsan",
                    "name": "张三"
                },
                "response_code": 201,
                "duration": 150,
                "created_at": "2024-01-01T12:00:00Z"
            }
        ],
        "total": 500,
        "page": 1,
        "page_size": 20,
        "total_pages": 25
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 5.2 获取审计日志详情

**端点**：`GET /api/v1/system/audit-logs/{id}/`

**描述**：获取审计日志详细信息

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1001,
        "user": {
            "id": 1,
            "username": "admin",
            "name": "系统管理员"
        },
        "module": "用户管理",
        "action": "create",
        "action_display": "创建",
        "description": "创建用户：zhangsan",
        "target_type": "User",
        "target_id": "10",
        "target_name": "张三",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "request_method": "POST",
        "request_url": "/api/v1/system/users/",
        "request_data": {
            "username": "zhangsan",
            "name": "张三",
            "email": "zhangsan@example.com"
        },
        "response_code": 201,
        "response_data": {
            "code": 201,
            "message": "创建成功",
            "data": {
                "id": 10,
                "username": "zhangsan"
            }
        },
        "duration": 150,
        "status": "success",
        "error_message": null,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 5.3 导出审计日志

**端点**：`GET /api/v1/system/audit-logs/export/`

**描述**：导出审计日志为Excel文件

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_time | string | 是 | 开始时间 |
| end_time | string | 是 | 结束时间 |
| module | string | 否 | 模块筛选 |
| format | string | 否 | 导出格式：xlsx/csv，默认xlsx |

**响应**：返回文件下载

---

### 5.4 获取操作统计

**端点**：`GET /api/v1/system/audit-logs/statistics/`

**描述**：获取审计日志统计数据

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_time | string | 是 | 开始时间 |
| end_time | string | 是 | 结束时间 |
| group_by | string | 否 | 分组方式：user/module/action |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "total": 1000,
        "by_module": [
            {"module": "用户管理", "count": 200},
            {"module": "委托管理", "count": 300},
            {"module": "样品管理", "count": 250},
            {"module": "报告管理", "count": 250}
        ],
        "by_action": [
            {"action": "create", "count": 400},
            {"action": "update", "count": 350},
            {"action": "delete", "count": 50},
            {"action": "login", "count": 200}
        ],
        "by_user": [
            {"user": "admin", "count": 500},
            {"user": "zhangsan", "count": 300},
            {"user": "lisi", "count": 200}
        ],
        "daily_trend": [
            {"date": "2024-01-01", "count": 50},
            {"date": "2024-01-02", "count": 60}
        ]
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 六、通知API

### 6.1 获取通知列表

**端点**：`GET /api/v1/system/notifications/`

**描述**：获取当前用户的通知列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| is_read | boolean | 否 | 是否已读 |
| type | string | 否 | 通知类型：system/task/approval/message |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "title": "新任务分配",
                "content": "您有一个新的检测任务待处理",
                "type": "task",
                "type_display": "任务通知",
                "is_read": false,
                "link": "/testing/tasks/123",
                "sender": {
                    "id": 1,
                    "name": "系统管理员"
                },
                "created_at": "2024-01-01T12:00:00Z"
            }
        ],
        "total": 50,
        "unread_count": 10,
        "page": 1,
        "page_size": 20,
        "total_pages": 3
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 6.2 获取未读通知数量

**端点**：`GET /api/v1/system/notifications/unread-count/`

**描述**：获取当前用户未读通知数量

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "total": 10,
        "by_type": {
            "system": 2,
            "task": 5,
            "approval": 3,
            "message": 0
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 6.3 标记通知已读

**端点**：`POST /api/v1/system/notifications/{id}/read/`

**描述**：标记指定通知为已读

**响应示例**：
```json
{
    "code": 200,
    "message": "已标记为已读",
    "data": {
        "id": 1,
        "is_read": true,
        "read_at": "2024-01-01T12:30:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 6.4 批量标记已读

**端点**：`POST /api/v1/system/notifications/batch-read/`

**描述**：批量标记通知为已读

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | 否 | 通知ID列表，为空则标记全部 |

**请求示例**：
```json
{
    "ids": [1, 2, 3, 4, 5]
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "已标记5条通知为已读",
    "data": {
        "updated_count": 5
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 6.5 删除通知

**端点**：`DELETE /api/v1/system/notifications/{id}/`

**描述**：删除指定通知

**响应示例**：
```json
{
    "code": 200,
    "message": "删除成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 6.6 发送通知

**端点**：`POST /api/v1/system/notifications/send/`

**描述**：发送通知给指定用户（需要权限）

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 通知标题 |
| content | string | 是 | 通知内容 |
| type | string | 是 | 通知类型 |
| user_ids | array | 是 | 接收用户ID列表 |
| link | string | 否 | 关联链接 |

**请求示例**：
```json
{
    "title": "系统维护通知",
    "content": "系统将于今晚22:00进行维护，预计持续2小时",
    "type": "system",
    "user_ids": [1, 2, 3, 4, 5],
    "link": "/announcements/123"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "通知发送成功",
    "data": {
        "sent_count": 5
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 七、部门管理API

### 7.1 获取部门列表

**端点**：`GET /api/v1/system/departments/`

**描述**：获取部门列表

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": [
        {
            "id": 1,
            "name": "信息中心",
            "code": "INFO",
            "parent_id": null,
            "manager": {
                "id": 1,
                "name": "系统管理员"
            },
            "user_count": 5,
            "children": [
                {
                    "id": 2,
                    "name": "开发组",
                    "code": "DEV",
                    "parent_id": 1,
                    "user_count": 3
                }
            ]
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 7.2 获取部门树

**端点**：`GET /api/v1/system/departments/tree/`

**描述**：获取部门树形结构

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": [
        {
            "id": 1,
            "name": "信息中心",
            "code": "INFO",
            "children": [
                {
                    "id": 2,
                    "name": "开发组",
                    "code": "DEV",
                    "children": []
                },
                {
                    "id": 3,
                    "name": "运维组",
                    "code": "OPS",
                    "children": []
                }
            ]
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 7.3 创建部门

**端点**：`POST /api/v1/system/departments/`

**描述**：创建新部门

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 部门名称 |
| code | string | 是 | 部门编码 |
| parent_id | integer | 否 | 上级部门ID |
| manager_id | integer | 否 | 部门负责人ID |
| description | string | 否 | 部门描述 |

**请求示例**：
```json
{
    "name": "检测一部",
    "code": "TEST1",
    "parent_id": 10,
    "manager_id": 5,
    "description": "负责化学检测"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 20,
        "name": "检测一部",
        "code": "TEST1",
        "parent_id": 10,
        "manager": {
            "id": 5,
            "name": "张三"
        },
        "created_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 7.4 更新部门

**端点**：`PUT /api/v1/system/departments/{id}/`

**描述**：更新部门信息

**请求示例**：
```json
{
    "name": "检测一部（更新）",
    "manager_id": 6,
    "description": "负责化学检测和物理检测"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "更新成功",
    "data": {
        "id": 20,
        "name": "检测一部（更新）",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 7.5 删除部门

**端点**：`DELETE /api/v1/system/departments/{id}/`

**描述**：删除部门

**响应示例**：
```json
{
    "code": 200,
    "message": "删除成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 0005 | 部门下有用户 | 先移除用户 |
| 0005 | 存在子部门 | 先删除子部门 |

---

## 八、系统配置API

### 8.1 获取系统配置

**端点**：`GET /api/v1/system/configs/`

**描述**：获取系统配置列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 配置分类 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": [
        {
            "id": 1,
            "key": "system.name",
            "value": "LIMIS实验室信息管理系统",
            "category": "基础配置",
            "description": "系统名称",
            "is_public": true
        },
        {
            "id": 2,
            "key": "system.logo",
            "value": "/media/logo.png",
            "category": "基础配置",
            "description": "系统Logo",
            "is_public": true
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 8.2 获取单个配置

**端点**：`GET /api/v1/system/configs/{key}/`

**描述**：获取指定配置项

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "key": "system.name",
        "value": "LIMIS实验室信息管理系统",
        "category": "基础配置",
        "description": "系统名称"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 8.3 更新配置

**端点**：`PUT /api/v1/system/configs/{key}/`

**描述**：更新配置项

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| value | string | 是 | 配置值 |

**请求示例**：
```json
{
    "value": "新的系统名称"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "更新成功",
    "data": {
        "key": "system.name",
        "value": "新的系统名称"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 九、错误码汇总

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
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
| 1001 | 用户名已存在 | 409 |
| 1002 | 邮箱已存在 | 409 |
| 1003 | 用户不存在 | 404 |
| 1004 | 密码错误 | 400 |
| 1005 | 用户已禁用 | 403 |
| 1006 | 用户已删除 | 410 |
| 1007 | 原密码错误 | 400 |
| 1008 | 新密码格式错误 | 400 |

---

*文档版本: v1.0.0*
*最后更新: 2024年*