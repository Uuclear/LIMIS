# 业务模块API

本文档描述LIMIS业务模块的API接口，包括委托管理、样品管理、检测任务、原始记录和报告管理等功能。

---

## 一、委托管理API

### 1.1 获取委托列表

**端点**：`GET /api/v1/commissions/`

**描述**：获取委托列表，支持分页、筛选和排序

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |
| search | string | 否 | 搜索关键词（编号/委托方/联系人） |
| status | string | 否 | 状态筛选 |
| commission_type | string | 否 | 委托类型 |
| client_id | integer | 否 | 委托方ID |
| created_at__gte | string | 否 | 创建时间起始 |
| created_at__lte | string | 否 | 创建时间结束 |
| ordering | string | 否 | 排序字段 |

**状态值说明**：

| 状态 | 说明 |
|------|------|
| draft | 草稿 |
| submitted | 已提交 |
| accepted | 已受理 |
| rejected | 已退回 |
| testing | 检测中 |
| completed | 已完成 |
| cancelled | 已取消 |

**请求示例**：
```http
GET /api/v1/commissions/?page=1&page_size=20&status=accepted&ordering=-created_at
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
                "commission_no": "WT2024010001",
                "commission_type": "regular",
                "commission_type_display": "常规委托",
                "status": "accepted",
                "status_display": "已受理",
                "client": {
                    "id": 10,
                    "name": "XX科技有限公司",
                    "contact": "张经理",
                    "phone": "13800138000"
                },
                "sample_count": 5,
                "test_item_count": 10,
                "expected_completion_date": "2024-02-01",
                "total_fee": 10000.00,
                "created_at": "2024-01-01T10:00:00Z",
                "created_by": {
                    "id": 1,
                    "name": "系统管理员"
                }
            }
        ],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.2 获取委托详情

**端点**：`GET /api/v1/commissions/{id}/`

**描述**：获取委托详细信息

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "commission_no": "WT2024010001",
        "commission_type": "regular",
        "commission_type_display": "常规委托",
        "status": "accepted",
        "status_display": "已受理",
        "client": {
            "id": 10,
            "name": "XX科技有限公司",
            "code": "CLIENT001",
            "contact": "张经理",
            "phone": "13800138000",
            "email": "zhang@example.com",
            "address": "北京市朝阳区xxx"
        },
        "samples": [
            {
                "id": 1,
                "sample_no": "YP2024010001",
                "name": "样品A",
                "sample_type": "固体",
                "quantity": 100,
                "unit": "g",
                "status": "received"
            }
        ],
        "test_items": [
            {
                "id": 1,
                "name": "重金属检测",
                "standard": "GB/T 5009.12",
                "method": "原子吸收法",
                "fee": 500.00
            }
        ],
        "sample_count": 5,
        "test_item_count": 10,
        "expected_completion_date": "2024-02-01",
        "actual_completion_date": null,
        "total_fee": 10000.00,
        "discount_rate": 0.95,
        "actual_fee": 9500.00,
        "payment_status": "unpaid",
        "payment_status_display": "未付款",
        "attachments": [
            {
                "id": 1,
                "name": "委托合同.pdf",
                "url": "/media/commissions/1/contract.pdf",
                "size": 102400
            }
        ],
        "remarks": "加急处理",
        "workflow": {
            "current_node": "检测中",
            "history": [
                {
                    "node": "提交",
                    "operator": "张三",
                    "operate_time": "2024-01-01T10:00:00Z",
                    "remarks": ""
                },
                {
                    "node": "受理",
                    "operator": "李四",
                    "operate_time": "2024-01-01T11:00:00Z",
                    "remarks": "符合受理条件"
                }
            ]
        },
        "created_at": "2024-01-01T10:00:00Z",
        "created_by": {
            "id": 1,
            "name": "系统管理员"
        },
        "updated_at": "2024-01-01T11:00:00Z",
        "updated_by": {
            "id": 2,
            "name": "李四"
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.3 创建委托

**端点**：`POST /api/v1/commissions/`

**描述**：创建新委托

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| commission_type | string | 是 | 委托类型：regular/urgent/special |
| client_id | integer | 是 | 委托方ID |
| expected_completion_date | string | 是 | 预计完成日期 |
| samples | array | 是 | 样品列表 |
| test_items | array | 是 | 检测项目列表 |
| discount_rate | number | 否 | 折扣率，默认1.0 |
| remarks | string | 否 | 备注 |
| attachments | array | 否 | 附件ID列表 |

**样品对象结构**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 样品名称 |
| sample_type | string | 是 | 样品类型 |
| quantity | number | 是 | 数量 |
| unit | string | 是 | 单位 |
| batch_no | string | 否 | 批号 |
| manufacturer | string | 否 | 生产厂家 |
| production_date | string | 否 | 生产日期 |
| expiry_date | string | 否 | 有效期 |
| storage_condition | string | 否 | 存储条件 |
| remarks | string | 否 | 备注 |

**检测项目对象结构**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 检测项目名称 |
| standard_id | integer | 是 | 检测标准ID |
| method_id | integer | 否 | 检测方法ID |
| fee | number | 是 | 费用 |

**请求示例**：
```json
{
    "commission_type": "regular",
    "client_id": 10,
    "expected_completion_date": "2024-02-01",
    "samples": [
        {
            "name": "样品A",
            "sample_type": "固体",
            "quantity": 100,
            "unit": "g",
            "batch_no": "B20240101",
            "manufacturer": "XX公司",
            "storage_condition": "常温"
        }
    ],
    "test_items": [
        {
            "name": "重金属检测",
            "standard_id": 1,
            "method_id": 1,
            "fee": 500.00
        }
    ],
    "discount_rate": 0.95,
    "remarks": "加急处理"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 1,
        "commission_no": "WT2024010001",
        "commission_type": "regular",
        "status": "draft",
        "client": {
            "id": 10,
            "name": "XX科技有限公司"
        },
        "sample_count": 1,
        "test_item_count": 1,
        "total_fee": 500.00,
        "actual_fee": 475.00,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误处理**：

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 2001 | 委托不存在 | 检查委托ID |
| 2002 | 委托状态不允许此操作 | 检查委托状态 |
| 2007 | 检测项目不能为空 | 添加检测项目 |
| 2008 | 样品信息不完整 | 完善样品信息 |

---

### 1.4 更新委托

**端点**：`PUT /api/v1/commissions/{id}/`

**描述**：更新委托信息（仅草稿状态可更新）

**请求示例**：
```json
{
    "expected_completion_date": "2024-02-15",
    "discount_rate": 0.90,
    "remarks": "更新备注"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "更新成功",
    "data": {
        "id": 1,
        "commission_no": "WT2024010001",
        "expected_completion_date": "2024-02-15",
        "discount_rate": 0.90,
        "actual_fee": 450.00,
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.5 提交委托

**端点**：`POST /api/v1/commissions/{id}/submit/`

**描述**：提交委托进行审核

**响应示例**：
```json
{
    "code": 200,
    "message": "提交成功",
    "data": {
        "id": 1,
        "commission_no": "WT2024010001",
        "status": "submitted",
        "status_display": "已提交",
        "submitted_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.6 受理委托

**端点**：`POST /api/v1/commissions/{id}/accept/`

**描述**：受理委托

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| remarks | string | 否 | 受理备注 |
| assignee_id | integer | 否 | 指定受理人 |

**请求示例**：
```json
{
    "remarks": "符合受理条件，开始安排检测"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "受理成功",
    "data": {
        "id": 1,
        "commission_no": "WT2024010001",
        "status": "accepted",
        "status_display": "已受理",
        "accepted_at": "2024-01-01T12:00:00Z",
        "accepted_by": {
            "id": 2,
            "name": "李四"
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.7 退回委托

**端点**：`POST /api/v1/commissions/{id}/reject/`

**描述**：退回委托

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | 是 | 退回原因 |

**请求示例**：
```json
{
    "reason": "样品信息不完整，请补充"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "退回成功",
    "data": {
        "id": 1,
        "commission_no": "WT2024010001",
        "status": "rejected",
        "status_display": "已退回",
        "rejected_at": "2024-01-01T12:00:00Z",
        "reject_reason": "样品信息不完整，请补充"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.8 取消委托

**端点**：`POST /api/v1/commissions/{id}/cancel/`

**描述**：取消委托

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | 是 | 取消原因 |

**响应示例**：
```json
{
    "code": 200,
    "message": "取消成功",
    "data": {
        "id": 1,
        "commission_no": "WT2024010001",
        "status": "cancelled",
        "status_display": "已取消"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.9 获取委托编号

**端点**：`GET /api/v1/commissions/next-number/`

**描述**：获取下一个委托编号

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "commission_no": "WT2024010002"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 1.10 导出委托

**端点**：`GET /api/v1/commissions/export/`

**描述**：导出委托列表为Excel文件

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | string | 否 | 委托ID列表，逗号分隔 |
| status | string | 否 | 状态筛选 |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| format | string | 否 | 导出格式：xlsx/csv |

**响应**：返回文件下载

---

## 二、样品管理API

### 2.1 获取样品列表

**端点**：`GET /api/v1/samples/`

**描述**：获取样品列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| search | string | 否 | 搜索关键词 |
| status | string | 否 | 状态筛选 |
| sample_type | string | 否 | 样品类型 |
| commission_id | integer | 否 | 委托ID |
| storage_location_id | integer | 否 | 存储位置ID |

**状态值说明**：

| 状态 | 说明 |
|------|------|
| pending | 待接收 |
| received | 已接收 |
| in_testing | 检测中 |
| completed | 已完成 |
| disposed | 已处置 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "sample_no": "YP2024010001",
                "name": "样品A",
                "sample_type": "固体",
                "quantity": 100,
                "unit": "g",
                "status": "received",
                "status_display": "已接收",
                "commission": {
                    "id": 1,
                    "commission_no": "WT2024010001"
                },
                "storage_location": {
                    "id": 1,
                    "name": "样品柜A-1层"
                },
                "received_at": "2024-01-01T10:00:00Z",
                "created_at": "2024-01-01T09:00:00Z"
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

### 2.2 获取样品详情

**端点**：`GET /api/v1/samples/{id}/`

**描述**：获取样品详细信息

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "sample_no": "YP2024010001",
        "name": "样品A",
        "sample_type": "固体",
        "quantity": 100,
        "unit": "g",
        "batch_no": "B20240101",
        "manufacturer": "XX公司",
        "production_date": "2024-01-01",
        "expiry_date": "2025-01-01",
        "storage_condition": "常温",
        "status": "received",
        "status_display": "已接收",
        "commission": {
            "id": 1,
            "commission_no": "WT2024010001",
            "client": {
                "id": 10,
                "name": "XX科技有限公司"
            }
        },
        "storage_location": {
            "id": 1,
            "name": "样品柜A-1层",
            "code": "A-1"
        },
        "test_items": [
            {
                "id": 1,
                "name": "重金属检测",
                "status": "pending"
            }
        ],
        "attachments": [
            {
                "id": 1,
                "name": "样品照片.jpg",
                "url": "/media/samples/1/photo.jpg"
            }
        ],
        "receive_info": {
            "received_at": "2024-01-01T10:00:00Z",
            "received_by": {
                "id": 3,
                "name": "王五"
            },
            "receive_remarks": "样品完好"
        },
        "dispose_info": null,
        "remarks": "",
        "created_at": "2024-01-01T09:00:00Z",
        "created_by": {
            "id": 1,
            "name": "系统管理员"
        },
        "updated_at": "2024-01-01T10:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.3 创建样品

**端点**：`POST /api/v1/samples/`

**描述**：创建新样品

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 样品名称 |
| sample_type | string | 是 | 样品类型 |
| quantity | number | 是 | 数量 |
| unit | string | 是 | 单位 |
| commission_id | integer | 是 | 委托ID |
| batch_no | string | 否 | 批号 |
| manufacturer | string | 否 | 生产厂家 |
| production_date | string | 否 | 生产日期 |
| expiry_date | string | 否 | 有效期 |
| storage_condition | string | 否 | 存储条件 |
| storage_location_id | integer | 否 | 存储位置ID |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "name": "样品B",
    "sample_type": "液体",
    "quantity": 500,
    "unit": "ml",
    "commission_id": 1,
    "batch_no": "B20240102",
    "manufacturer": "YY公司",
    "storage_condition": "冷藏"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 2,
        "sample_no": "YP2024010002",
        "name": "样品B",
        "sample_type": "液体",
        "quantity": 500,
        "unit": "ml",
        "status": "pending",
        "created_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.4 接收样品

**端点**：`POST /api/v1/samples/{id}/receive/`

**描述**：接收样品

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| storage_location_id | integer | 是 | 存储位置ID |
| actual_quantity | number | 否 | 实际数量 |
| condition | string | 否 | 样品状态：good/damaged/abnormal |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "storage_location_id": 1,
    "actual_quantity": 100,
    "condition": "good",
    "remarks": "样品完好"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "接收成功",
    "data": {
        "id": 1,
        "sample_no": "YP2024010001",
        "status": "received",
        "status_display": "已接收",
        "storage_location": {
            "id": 1,
            "name": "样品柜A-1层"
        },
        "received_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.5 流转样品

**端点**：`POST /api/v1/samples/{id}/transfer/`

**描述**：流转样品到下一环节

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| target_location_id | integer | 是 | 目标位置ID |
| target_user_id | integer | 否 | 目标接收人ID |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "target_location_id": 2,
    "target_user_id": 5,
    "remarks": "流转到检测室"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "流转成功",
    "data": {
        "id": 1,
        "sample_no": "YP2024010001",
        "status": "in_testing",
        "transfer_record": {
            "from_location": "样品柜A-1层",
            "to_location": "检测室B-2",
            "transferred_at": "2024-01-01T12:00:00Z",
            "transferred_by": {
                "id": 3,
                "name": "王五"
            }
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.6 处置样品

**端点**：`POST /api/v1/samples/{id}/dispose/`

**描述**：处置样品

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dispose_method | string | 是 | 处置方式：return/destroy/other |
| dispose_reason | string | 是 | 处置原因 |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "dispose_method": "destroy",
    "dispose_reason": "检测完成，按规定销毁",
    "remarks": "已填写处置记录"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "处置成功",
    "data": {
        "id": 1,
        "sample_no": "YP2024010001",
        "status": "disposed",
        "status_display": "已处置",
        "disposed_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.7 样品二维码

**端点**：`GET /api/v1/samples/{id}/qrcode/`

**描述**：获取样品二维码

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| size | integer | 否 | 二维码尺寸，默认200 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "sample_no": "YP2024010001",
        "qrcode_url": "/media/samples/1/qrcode.png",
        "content": "SAMPLE:YP2024010001"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2.8 扫码查询样品

**端点**：`GET /api/v1/samples/scan/`

**描述**：通过二维码查询样品

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 二维码内容 |

**请求示例**：
```http
GET /api/v1/samples/scan/?code=SAMPLE:YP2024010001
```

**响应示例**：
```json
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "id": 1,
        "sample_no": "YP2024010001",
        "name": "样品A",
        "status": "received"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 三、检测任务API

### 3.1 获取任务列表

**端点**：`GET /api/v1/testing/tasks/`

**描述**：获取检测任务列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| search | string | 否 | 搜索关键词 |
| status | string | 否 | 状态筛选 |
| assignee_id | integer | 否 | 分配人ID |
| tester_id | integer | 否 | 检测人员ID |
| commission_id | integer | 否 | 委托ID |
| priority | string | 否 | 优先级 |

**状态值说明**：

| 状态 | 说明 |
|------|------|
| pending | 待分配 |
| assigned | 已分配 |
| in_progress | 进行中 |
| completed | 已完成 |
| cancelled | 已取消 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "task_no": "RW2024010001",
                "name": "重金属检测任务",
                "status": "in_progress",
                "status_display": "进行中",
                "priority": "high",
                "priority_display": "高",
                "commission": {
                    "id": 1,
                    "commission_no": "WT2024010001"
                },
                "sample": {
                    "id": 1,
                    "sample_no": "YP2024010001",
                    "name": "样品A"
                },
                "test_item": {
                    "id": 1,
                    "name": "重金属检测"
                },
                "tester": {
                    "id": 5,
                    "name": "检测员张三"
                },
                "equipment": {
                    "id": 1,
                    "name": "原子吸收光谱仪"
                },
                "planned_start_date": "2024-01-02",
                "planned_end_date": "2024-01-05",
                "actual_start_date": "2024-01-02",
                "actual_end_date": null,
                "progress": 60,
                "created_at": "2024-01-01T10:00:00Z"
            }
        ],
        "total": 30,
        "page": 1,
        "page_size": 20,
        "total_pages": 2
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.2 获取任务详情

**端点**：`GET /api/v1/testing/tasks/{id}/`

**描述**：获取任务详细信息

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "task_no": "RW2024010001",
        "name": "重金属检测任务",
        "description": "对样品A进行重金属含量检测",
        "status": "in_progress",
        "status_display": "进行中",
        "priority": "high",
        "priority_display": "高",
        "commission": {
            "id": 1,
            "commission_no": "WT2024010001",
            "client": {
                "id": 10,
                "name": "XX科技有限公司"
            }
        },
        "sample": {
            "id": 1,
            "sample_no": "YP2024010001",
            "name": "样品A",
            "sample_type": "固体",
            "quantity": 100,
            "unit": "g"
        },
        "test_item": {
            "id": 1,
            "name": "重金属检测",
            "standard": {
                "id": 1,
                "name": "GB/T 5009.12",
                "title": "食品中铅的测定"
            },
            "method": {
                "id": 1,
                "name": "原子吸收法"
            }
        },
        "tester": {
            "id": 5,
            "name": "检测员张三",
            "department": "检测一部"
        },
        "equipment": {
            "id": 1,
            "name": "原子吸收光谱仪",
            "code": "EQ001",
            "status": "normal"
        },
        "planned_start_date": "2024-01-02",
        "planned_end_date": "2024-01-05",
        "actual_start_date": "2024-01-02",
        "actual_end_date": null,
        "progress": 60,
        "records": [
            {
                "id": 1,
                "record_no": "JL2024010001",
                "name": "原始记录1",
                "status": "completed",
                "created_at": "2024-01-02T10:00:00Z"
            }
        ],
        "attachments": [
            {
                "id": 1,
                "name": "检测数据.xlsx",
                "url": "/media/tasks/1/data.xlsx"
            }
        ],
        "remarks": "",
        "created_at": "2024-01-01T10:00:00Z",
        "created_by": {
            "id": 2,
            "name": "李四"
        },
        "updated_at": "2024-01-02T10:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.3 创建任务

**端点**：`POST /api/v1/testing/tasks/`

**描述**：创建检测任务

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 任务名称 |
| commission_id | integer | 是 | 委托ID |
| sample_id | integer | 是 | 样品ID |
| test_item_id | integer | 是 | 检测项目ID |
| tester_id | integer | 否 | 检测人员ID |
| equipment_id | integer | 否 | 设备ID |
| priority | string | 否 | 优先级：low/medium/high/urgent |
| planned_start_date | string | 是 | 计划开始日期 |
| planned_end_date | string | 是 | 计划结束日期 |
| description | string | 否 | 任务描述 |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "name": "重金属检测任务",
    "commission_id": 1,
    "sample_id": 1,
    "test_item_id": 1,
    "tester_id": 5,
    "equipment_id": 1,
    "priority": "high",
    "planned_start_date": "2024-01-02",
    "planned_end_date": "2024-01-05",
    "description": "对样品A进行重金属含量检测"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 1,
        "task_no": "RW2024010001",
        "name": "重金属检测任务",
        "status": "pending",
        "created_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.4 分配任务

**端点**：`POST /api/v1/testing/tasks/{id}/assign/`

**描述**：分配任务给检测人员

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tester_id | integer | 是 | 检测人员ID |
| equipment_id | integer | 否 | 设备ID |
| planned_start_date | string | 否 | 计划开始日期 |
| planned_end_date | string | 否 | 计划结束日期 |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "tester_id": 5,
    "equipment_id": 1,
    "planned_start_date": "2024-01-02",
    "planned_end_date": "2024-01-05",
    "remarks": "请按时完成"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "分配成功",
    "data": {
        "id": 1,
        "task_no": "RW2024010001",
        "status": "assigned",
        "status_display": "已分配",
        "tester": {
            "id": 5,
            "name": "检测员张三"
        },
        "assigned_at": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.5 开始任务

**端点**：`POST /api/v1/testing/tasks/{id}/start/`

**描述**：开始执行任务

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| equipment_id | integer | 否 | 设备ID |
| remarks | string | 否 | 备注 |

**响应示例**：
```json
{
    "code": 200,
    "message": "任务已开始",
    "data": {
        "id": 1,
        "task_no": "RW2024010001",
        "status": "in_progress",
        "status_display": "进行中",
        "actual_start_date": "2024-01-02",
        "started_at": "2024-01-02T09:00:00Z"
    },
    "timestamp": "2024-01-02T09:00:00Z"
}
```

---

### 3.6 更新任务进度

**端点**：`POST /api/v1/testing/tasks/{id}/progress/`

**描述**：更新任务进度

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| progress | integer | 是 | 进度百分比（0-100） |
| remarks | string | 否 | 进度说明 |

**请求示例**：
```json
{
    "progress": 60,
    "remarks": "已完成样品前处理和标准曲线绘制"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "进度更新成功",
    "data": {
        "id": 1,
        "task_no": "RW2024010001",
        "progress": 60,
        "updated_at": "2024-01-02T15:00:00Z"
    },
    "timestamp": "2024-01-02T15:00:00Z"
}
```

---

### 3.7 完成任务

**端点**：`POST /api/v1/testing/tasks/{id}/complete/`

**描述**：完成任务

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| result_summary | string | 否 | 结果摘要 |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "result_summary": "重金属含量符合标准要求",
    "remarks": "检测完成，数据已记录"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "任务已完成",
    "data": {
        "id": 1,
        "task_no": "RW2024010001",
        "status": "completed",
        "status_display": "已完成",
        "actual_end_date": "2024-01-05",
        "completed_at": "2024-01-05T17:00:00Z"
    },
    "timestamp": "2024-01-05T17:00:00Z"
}
```

---

### 3.8 取消任务

**端点**：`POST /api/v1/testing/tasks/{id}/cancel/`

**描述**：取消任务

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | 是 | 取消原因 |

**响应示例**：
```json
{
    "code": 200,
    "message": "任务已取消",
    "data": {
        "id": 1,
        "task_no": "RW2024010001",
        "status": "cancelled",
        "status_display": "已取消"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.9 获取我的任务

**端点**：`GET /api/v1/testing/tasks/my/`

**描述**：获取当前用户的任务列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 状态筛选 |
| priority | string | 否 | 优先级筛选 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "task_no": "RW2024010001",
                "name": "重金属检测任务",
                "status": "in_progress",
                "priority": "high",
                "progress": 60,
                "planned_end_date": "2024-01-05"
            }
        ],
        "total": 5,
        "statistics": {
            "pending": 2,
            "in_progress": 2,
            "completed": 1
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 四、原始记录API

### 4.1 获取记录列表

**端点**：`GET /api/v1/testing/records/`

**描述**：获取原始记录列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| search | string | 否 | 搜索关键词 |
| status | string | 否 | 状态筛选 |
| task_id | integer | 否 | 任务ID |
| tester_id | integer | 否 | 检测人员ID |
| record_type | string | 否 | 记录类型 |

**状态值说明**：

| 状态 | 说明 |
|------|------|
| draft | 草稿 |
| submitted | 已提交 |
| reviewed | 已审核 |
| approved | 已批准 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "record_no": "JL2024010001",
                "name": "重金属检测原始记录",
                "record_type": "detection",
                "record_type_display": "检测记录",
                "status": "reviewed",
                "status_display": "已审核",
                "task": {
                    "id": 1,
                    "task_no": "RW2024010001",
                    "name": "重金属检测任务"
                },
                "tester": {
                    "id": 5,
                    "name": "检测员张三"
                },
                "test_date": "2024-01-03",
                "created_at": "2024-01-03T10:00:00Z"
            }
        ],
        "total": 20,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 4.2 获取记录详情

**端点**：`GET /api/v1/testing/records/{id}/`

**描述**：获取原始记录详细信息

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "record_no": "JL2024010001",
        "name": "重金属检测原始记录",
        "record_type": "detection",
        "record_type_display": "检测记录",
        "status": "reviewed",
        "status_display": "已审核",
        "task": {
            "id": 1,
            "task_no": "RW2024010001",
            "name": "重金属检测任务",
            "sample": {
                "id": 1,
                "sample_no": "YP2024010001",
                "name": "样品A"
            }
        },
        "tester": {
            "id": 5,
            "name": "检测员张三",
            "department": "检测一部"
        },
        "equipment": {
            "id": 1,
            "name": "原子吸收光谱仪",
            "code": "EQ001"
        },
        "test_method": {
            "id": 1,
            "name": "原子吸收法",
            "standard": "GB/T 5009.12"
        },
        "test_date": "2024-01-03",
        "test_environment": {
            "temperature": "25",
            "humidity": "60",
            "other": ""
        },
        "test_data": {
            "sample_info": {
                "sample_no": "YP2024010001",
                "sample_name": "样品A",
                "sample_quantity": "100g"
            },
            "test_conditions": {
                "instrument": "原子吸收光谱仪",
                "wavelength": "283.3nm",
                "slit_width": "0.4nm"
            },
            "standard_curve": {
                "concentrations": [0, 1, 2, 5, 10],
                "absorbances": [0.001, 0.098, 0.195, 0.488, 0.975],
                "correlation_coefficient": 0.9998
            },
            "sample_results": [
                {
                    "sample_id": 1,
                    "sample_name": "样品A-1",
                    "absorbance": 0.245,
                    "concentration": 2.5,
                    "unit": "mg/kg"
                }
            ]
        },
        "conclusion": "样品重金属含量符合标准要求",
        "review_info": {
            "reviewer": {
                "id": 6,
                "name": "审核员李四"
            },
            "reviewed_at": "2024-01-04T10:00:00Z",
            "review_opinion": "数据完整，结果准确"
        },
        "approve_info": null,
        "attachments": [
            {
                "id": 1,
                "name": "检测图谱.pdf",
                "url": "/media/records/1/chart.pdf"
            }
        ],
        "created_at": "2024-01-03T10:00:00Z",
        "created_by": {
            "id": 5,
            "name": "检测员张三"
        },
        "updated_at": "2024-01-04T10:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 4.3 创建记录

**端点**：`POST /api/v1/testing/records/`

**描述**：创建原始记录

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 记录名称 |
| record_type | string | 是 | 记录类型 |
| task_id | integer | 是 | 任务ID |
| equipment_id | integer | 否 | 设备ID |
| test_method_id | integer | 否 | 检测方法ID |
| test_date | string | 是 | 检测日期 |
| test_environment | object | 否 | 检测环境 |
| test_data | object | 是 | 检测数据 |
| conclusion | string | 否 | 结论 |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "name": "重金属检测原始记录",
    "record_type": "detection",
    "task_id": 1,
    "equipment_id": 1,
    "test_method_id": 1,
    "test_date": "2024-01-03",
    "test_environment": {
        "temperature": "25",
        "humidity": "60"
    },
    "test_data": {
        "sample_results": [
            {
                "sample_name": "样品A-1",
                "absorbance": 0.245,
                "concentration": 2.5,
                "unit": "mg/kg"
            }
        ]
    },
    "conclusion": "样品重金属含量符合标准要求"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 1,
        "record_no": "JL2024010001",
        "name": "重金属检测原始记录",
        "status": "draft",
        "created_at": "2024-01-03T10:00:00Z"
    },
    "timestamp": "2024-01-03T10:00:00Z"
}
```

---

### 4.4 提交记录

**端点**：`POST /api/v1/testing/records/{id}/submit/`

**描述**：提交记录进行审核

**响应示例**：
```json
{
    "code": 200,
    "message": "提交成功",
    "data": {
        "id": 1,
        "record_no": "JL2024010001",
        "status": "submitted",
        "status_display": "已提交",
        "submitted_at": "2024-01-03T15:00:00Z"
    },
    "timestamp": "2024-01-03T15:00:00Z"
}
```

---

### 4.5 审核记录

**端点**：`POST /api/v1/testing/records/{id}/review/`

**描述**：审核记录

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| passed | boolean | 是 | 是否通过 |
| opinion | string | 否 | 审核意见 |

**请求示例**：
```json
{
    "passed": true,
    "opinion": "数据完整，结果准确"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "审核成功",
    "data": {
        "id": 1,
        "record_no": "JL2024010001",
        "status": "reviewed",
        "status_display": "已审核",
        "reviewed_at": "2024-01-04T10:00:00Z"
    },
    "timestamp": "2024-01-04T10:00:00Z"
}
```

---

### 4.6 批准记录

**端点**：`POST /api/v1/testing/records/{id}/approve/`

**描述**：批准记录

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| passed | boolean | 是 | 是否通过 |
| opinion | string | 否 | 批准意见 |

**响应示例**：
```json
{
    "code": 200,
    "message": "批准成功",
    "data": {
        "id": 1,
        "record_no": "JL2024010001",
        "status": "approved",
        "status_display": "已批准",
        "approved_at": "2024-01-05T10:00:00Z"
    },
    "timestamp": "2024-01-05T10:00:00Z"
}
```

---

### 4.7 导出记录

**端点**：`GET /api/v1/testing/records/{id}/export/`

**描述**：导出原始记录为PDF

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 否 | 导出格式：pdf/docx |

**响应**：返回文件下载

---

## 五、报告管理API

### 5.1 获取报告列表

**端点**：`GET /api/v1/reports/`

**描述**：获取检测报告列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| search | string | 否 | 搜索关键词 |
| status | string | 否 | 状态筛选 |
| report_type | string | 否 | 报告类型 |
| commission_id | integer | 否 | 委托ID |

**状态值说明**：

| 状态 | 说明 |
|------|------|
| draft | 草稿 |
| submitted | 已提交 |
| reviewed | 已审核 |
| approved | 已批准 |
| issued | 已签发 |
| cancelled | 已作废 |

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": 1,
                "report_no": "BG2024010001",
                "title": "重金属检测报告",
                "report_type": "regular",
                "report_type_display": "常规报告",
                "status": "issued",
                "status_display": "已签发",
                "commission": {
                    "id": 1,
                    "commission_no": "WT2024010001",
                    "client": {
                        "id": 10,
                        "name": "XX科技有限公司"
                    }
                },
                "issued_date": "2024-01-10",
                "valid_until": "2025-01-10",
                "created_at": "2024-01-05T10:00:00Z"
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

### 5.2 获取报告详情

**端点**：`GET /api/v1/reports/{id}/`

**描述**：获取报告详细信息

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "title": "重金属检测报告",
        "report_type": "regular",
        "report_type_display": "常规报告",
        "status": "issued",
        "status_display": "已签发",
        "commission": {
            "id": 1,
            "commission_no": "WT2024010001",
            "commission_type": "regular",
            "client": {
                "id": 10,
                "name": "XX科技有限公司",
                "contact": "张经理",
                "phone": "13800138000",
                "address": "北京市朝阳区xxx"
            }
        },
        "samples": [
            {
                "id": 1,
                "sample_no": "YP2024010001",
                "name": "样品A",
                "sample_type": "固体",
                "quantity": 100,
                "unit": "g"
            }
        ],
        "test_items": [
            {
                "id": 1,
                "name": "重金属检测",
                "standard": "GB/T 5009.12",
                "method": "原子吸收法",
                "result": "合格",
                "conclusion": "符合标准要求"
            }
        ],
        "test_results": [
            {
                "sample_no": "YP2024010001",
                "sample_name": "样品A",
                "test_item": "铅(Pb)",
                "standard_limit": "≤0.5 mg/kg",
                "test_result": "0.25 mg/kg",
                "conclusion": "合格"
            }
        ],
        "conclusion": "经检测，所送样品的重金属含量符合相关标准要求。",
        "issued_date": "2024-01-10",
        "valid_until": "2025-01-10",
        "issuer": {
            "id": 1,
            "name": "签发人王五",
            "title": "技术负责人"
        },
        "reviewer": {
            "id": 2,
            "name": "审核员李四",
            "title": "质量负责人"
        },
        "tester": {
            "id": 5,
            "name": "检测员张三",
            "title": "检测工程师"
        },
        "attachments": [
            {
                "id": 1,
                "name": "检测报告.pdf",
                "url": "/media/reports/1/report.pdf"
            }
        ],
        "print_count": 2,
        "last_print_at": "2024-01-15T10:00:00Z",
        "created_at": "2024-01-05T10:00:00Z",
        "created_by": {
            "id": 5,
            "name": "检测员张三"
        },
        "updated_at": "2024-01-10T15:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 5.3 创建报告

**端点**：`POST /api/v1/reports/`

**描述**：创建检测报告

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 报告标题 |
| report_type | string | 是 | 报告类型：regular/urgent/special |
| commission_id | integer | 是 | 委托ID |
| template_id | integer | 否 | 报告模板ID |
| test_results | array | 是 | 检测结果列表 |
| conclusion | string | 是 | 结论 |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "title": "重金属检测报告",
    "report_type": "regular",
    "commission_id": 1,
    "template_id": 1,
    "test_results": [
        {
            "sample_id": 1,
            "test_item": "铅(Pb)",
            "standard_limit": "≤0.5 mg/kg",
            "test_result": "0.25 mg/kg",
            "conclusion": "合格"
        }
    ],
    "conclusion": "经检测，所送样品的重金属含量符合相关标准要求。"
}
```

**响应示例**：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "title": "重金属检测报告",
        "status": "draft",
        "created_at": "2024-01-05T10:00:00Z"
    },
    "timestamp": "2024-01-05T10:00:00Z"
}
```

---

### 5.4 提交报告

**端点**：`POST /api/v1/reports/{id}/submit/`

**描述**：提交报告进行审核

**响应示例**：
```json
{
    "code": 200,
    "message": "提交成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "status": "submitted",
        "status_display": "已提交",
        "submitted_at": "2024-01-06T10:00:00Z"
    },
    "timestamp": "2024-01-06T10:00:00Z"
}
```

---

### 5.5 审核报告

**端点**：`POST /api/v1/reports/{id}/review/`

**描述**：审核报告

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| passed | boolean | 是 | 是否通过 |
| opinion | string | 否 | 审核意见 |

**请求示例**：
```json
{
    "passed": true,
    "opinion": "报告内容完整，数据准确"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "审核成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "status": "reviewed",
        "status_display": "已审核",
        "reviewed_at": "2024-01-07T10:00:00Z"
    },
    "timestamp": "2024-01-07T10:00:00Z"
}
```

---

### 5.6 批准报告

**端点**：`POST /api/v1/reports/{id}/approve/`

**描述**：批准报告

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| passed | boolean | 是 | 是否通过 |
| opinion | string | 否 | 批准意见 |

**响应示例**：
```json
{
    "code": 200,
    "message": "批准成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "status": "approved",
        "status_display": "已批准",
        "approved_at": "2024-01-08T10:00:00Z"
    },
    "timestamp": "2024-01-08T10:00:00Z"
}
```

---

### 5.7 签发报告

**端点**：`POST /api/v1/reports/{id}/issue/`

**描述**：签发报告

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| issued_date | string | 否 | 签发日期，默认当天 |
| valid_months | integer | 否 | 有效期月数，默认12 |

**响应示例**：
```json
{
    "code": 200,
    "message": "签发成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "status": "issued",
        "status_display": "已签发",
        "issued_date": "2024-01-10",
        "valid_until": "2025-01-10",
        "issued_at": "2024-01-10T15:00:00Z"
    },
    "timestamp": "2024-01-10T15:00:00Z"
}
```

---

### 5.8 作废报告

**端点**：`POST /api/v1/reports/{id}/cancel/`

**描述**：作废报告

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | 是 | 作废原因 |

**请求示例**：
```json
{
    "reason": "检测数据有误，需要重新出具报告"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "作废成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "status": "cancelled",
        "status_display": "已作废",
        "cancelled_at": "2024-01-15T10:00:00Z"
    },
    "timestamp": "2024-01-15T10:00:00Z"
}
```

---

### 5.9 打印报告

**端点**：`POST /api/v1/reports/{id}/print/`

**描述**：打印报告（记录打印次数）

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| copies | integer | 否 | 打印份数，默认1 |

**响应示例**：
```json
{
    "code": 200,
    "message": "打印成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "print_count": 3,
        "last_print_at": "2024-01-15T10:00:00Z"
    },
    "timestamp": "2024-01-15T10:00:00Z"
}
```

---

### 5.10 下载报告

**端点**：`GET /api/v1/reports/{id}/download/`

**描述**：下载报告PDF文件

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 否 | 下载格式：pdf/docx |

**响应**：返回文件下载

---

### 5.11 发送报告

**端点**：`POST /api/v1/reports/{id}/send/`

**描述**：发送报告给委托方

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| send_method | string | 是 | 发送方式：email/mail/in_person |
| recipient | string | 否 | 收件人（邮件发送时） |
| address | string | 否 | 邮寄地址（邮寄时） |
| remarks | string | 否 | 备注 |

**请求示例**：
```json
{
    "send_method": "email",
    "recipient": "zhang@example.com",
    "remarks": "已发送电子版报告"
}
```

**响应示例**：
```json
{
    "code": 200,
    "message": "发送成功",
    "data": {
        "id": 1,
        "report_no": "BG2024010001",
        "send_record": {
            "method": "email",
            "recipient": "zhang@example.com",
            "sent_at": "2024-01-15T10:00:00Z"
        }
    },
    "timestamp": "2024-01-15T10:00:00Z"
}
```

---

### 5.12 报告二维码

**端点**：`GET /api/v1/reports/{id}/qrcode/`

**描述**：获取报告二维码（用于报告真伪查询）

**响应示例**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "report_no": "BG2024010001",
        "qrcode_url": "/media/reports/1/qrcode.png",
        "verify_url": "https://example.com/verify/BG2024010001"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 5.13 报告验证

**端点**：`GET /api/v1/reports/verify/{report_no}/`

**描述**：验证报告真伪（公开接口，无需认证）

**响应示例**：
```json
{
    "code": 200,
    "message": "验证成功",
    "data": {
        "valid": true,
        "report_no": "BG2024010001",
        "title": "重金属检测报告",
        "client": "XX科技有限公司",
        "issued_date": "2024-01-10",
        "valid_until": "2025-01-10",
        "status": "有效"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 六、错误码汇总

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
| 3001 | 样品不存在 | 404 |
| 3002 | 样品状态不允许此操作 | 400 |
| 3003 | 样品编号已存在 | 409 |
| 3004 | 样品已接收 | 409 |
| 3005 | 样品已流转 | 409 |
| 3006 | 样品已处置 | 410 |
| 3007 | 样品数量不足 | 400 |
| 3008 | 样品位置冲突 | 409 |
| 4001 | 任务不存在 | 404 |
| 4002 | 任务状态不允许此操作 | 400 |
| 4003 | 任务已分配 | 409 |
| 4004 | 任务已开始 | 409 |
| 4005 | 任务已完成 | 409 |
| 4006 | 任务已取消 | 410 |
| 4007 | 检测人员不可用 | 400 |
| 4008 | 设备不可用 | 400 |
| 5001 | 报告不存在 | 404 |
| 5002 | 报告状态不允许此操作 | 400 |
| 5003 | 报告已提交 | 409 |
| 5004 | 报告已审核 | 409 |
| 5005 | 报告已签发 | 409 |
| 5006 | 报告已作废 | 410 |
| 5007 | 报告编号已存在 | 409 |
| 5008 | 报告模板不存在 | 404 |

---

*文档版本: v1.0.0*
*最后更新: 2024年*