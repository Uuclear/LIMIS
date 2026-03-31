# 支撑模块API

本文档介绍支撑模块的API接口。

---

## 一、设备管理API

### 1.1 设备列表

```
GET /api/v1/equipment/

参数：
- page: 页码
- page_size: 每页数量
- search: 搜索关键词
- status: 状态筛选
- category: 分类筛选

响应：
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "equipment_no": "EQ-20260301-001",
      "name": "万能试验机",
      "model": "WDW-100",
      "category": "A",
      "status": "in_use",
      "calibration_valid_until": "2026-12-31"
    }
  ]
}
```

### 1.2 设备详情

```
GET /api/v1/equipment/{id}/

响应：
{
  "id": 1,
  "equipment_no": "EQ-20260301-001",
  "name": "万能试验机",
  "model": "WDW-100",
  "manufacturer": "XX公司",
  "category": "A",
  "status": "in_use",
  "location": "力学实验室",
  "keeper": "张三",
  "calibrations": [...],
  "maintenances": [...]
}
```

### 1.3 校准记录

```
GET /api/v1/equipment/{id}/calibrations/

POST /api/v1/equipment/{id}/calibrations/
请求体：
{
  "calibration_date": "2026-03-01",
  "certificate_no": "C20260301-001",
  "calibration_org": "计量院",
  "result": "pass",
  "valid_until": "2027-03-01"
}
```

---

## 二、人员管理API

### 2.1 人员列表

```
GET /api/v1/staff/profiles/

参数：
- department: 部门筛选
- status: 状态筛选

响应：
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "employee_no": "EMP001",
      "name": "张三",
      "department": "检测部",
      "position": "检测员",
      "status": "active"
    }
  ]
}
```

### 2.2 证书管理

```
GET /api/v1/staff/certificates/

POST /api/v1/staff/certificates/
请求体：
{
  "staff": 1,
  "cert_type": "上岗证",
  "cert_name": "混凝土检测上岗证",
  "cert_no": "SG2026001",
  "issue_date": "2026-01-01",
  "expiry_date": "2029-01-01"
}
```

### 2.3 人员授权

```
GET /api/v1/staff/authorizations/

POST /api/v1/staff/authorizations/
请求体：
{
  "staff": 1,
  "test_category": "混凝土",
  "test_methods": [1, 2, 3],
  "authorized_date": "2026-03-01",
  "expiry_date": "2027-03-01"
}
```

---

## 三、标准规范API

### 3.1 标准列表

```
GET /api/v1/standards/

参数：
- standard_type: 标准类型
- status: 状态
- applicable_field: 适用领域

响应：
{
  "count": 200,
  "results": [
    {
      "id": 1,
      "standard_no": "GB/T 50081",
      "name": "混凝土物理力学性能试验方法标准",
      "standard_type": "national",
      "status": "active",
      "issue_date": "2019-01-01"
    }
  ]
}
```

### 3.2 检测方法

```
GET /api/v1/standards/methods/

POST /api/v1/standards/methods/
请求体：
{
  "method_no": "M001",
  "name": "混凝土抗压强度试验",
  "standard": 1,
  "test_category": "混凝土",
  "is_active": true
}
```

### 3.3 方法验证

```
GET /api/v1/standards/validations/

POST /api/v1/standards/validations/
请求体：
{
  "method": 1,
  "validation_date": "2026-03-01",
  "validator": "张三",
  "result": "pass",
  "report": "验证报告.pdf"
}
```

---

## 四、质量管理API

### 4.1 内部审核

```
GET /api/v1/quality/audits/

POST /api/v1/quality/audits/
请求体：
{
  "audit_no": "AUD-2026-001",
  "title": "2026年第一季度内部审核",
  "audit_type": "routine",
  "planned_date": "2026-03-15",
  "auditors": [1, 2, 3]
}
```

### 4.2 审核发现

```
GET /api/v1/quality/audit-findings/

POST /api/v1/quality/audit-findings/
请求体：
{
  "audit": 1,
  "finding_type": "nonconformity",
  "description": "发现不符合项",
  "clause": "4.2.1",
  "severity": "major"
}
```

### 4.3 纠正措施

```
GET /api/v1/quality/corrective-actions/

POST /api/v1/quality/corrective-actions/
请求体：
{
  "finding": 1,
  "root_cause": "原因分析",
  "action": "纠正措施",
  "responsible": 1,
  "due_date": "2026-04-01"
}
```

### 4.4 管理评审

```
GET /api/v1/quality/reviews/

POST /api/v1/quality/reviews/
请求体：
{
  "review_no": "MR-2026-001",
  "title": "2026年度管理评审",
  "review_date": "2026-12-15",
  "chairman": 1,
  "participants": [1, 2, 3]
}
```

### 4.5 不符合项

```
GET /api/v1/quality/nonconformities/

POST /api/v1/quality/nonconformities/
请求体：
{
  "nc_no": "NC-2026-001",
  "source": "internal_audit",
  "description": "不符合项描述",
  "severity": "major",
  "status": "open"
}
```

### 4.6 投诉管理

```
GET /api/v1/quality/complaints/

POST /api/v1/quality/complaints/
请求体：
{
  "complaint_no": "CP-2026-001",
  "complainant": "张三",
  "contact": "13800138000",
  "content": "投诉内容",
  "complaint_date": "2026-03-01"
}
```

---

## 五、耗材管理API

### 5.1 耗材列表

```
GET /api/v1/consumables/items/

参数：
- category: 分类
- low_stock: 是否低库存

响应：
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "item_no": "HC-001",
      "name": "标准砂",
      "specification": "ISO标准砂",
      "unit": "kg",
      "stock_quantity": 50,
      "safety_stock": 20
    }
  ]
}
```

### 5.2 入库记录

```
GET /api/v1/consumables/in-records/

POST /api/v1/consumables/in-records/
请求体：
{
  "item": 1,
  "quantity": 100,
  "supplier": 1,
  "batch_no": "B20260301",
  "in_date": "2026-03-01",
  "receiver": 1
}
```

### 5.3 出库记录

```
GET /api/v1/consumables/out-records/

POST /api/v1/consumables/out-records/
请求体：
{
  "item": 1,
  "quantity": 10,
  "purpose": "检测使用",
  "recipient": 1,
  "out_date": "2026-03-01"
}
```

### 5.4 供应商

```
GET /api/v1/consumables/suppliers/

POST /api/v1/consumables/suppliers/
请求体：
{
  "name": "XX供应商",
  "contact": "张三",
  "phone": "13800138000",
  "address": "上海市",
  "is_qualified": true
}
```

---

## 六、统计分析API

### 6.1 仪表盘数据

```
GET /api/v1/statistics/dashboard/

响应：
{
  "pending_tasks": 10,
  "pending_reviews": 5,
  "pending_audits": 3,
  "equipment_alerts": 2,
  "sample_alerts": 1,
  "monthly_tests": 150,
  "monthly_reports": 120
}
```

### 6.2 检测量统计

```
GET /api/v1/statistics/test-volume/

参数：
- period: day/week/month
- start_date: 开始日期
- end_date: 结束日期

响应：
{
  "labels": ["2026-03-01", "2026-03-02", ...],
  "data": [10, 15, 12, ...]
}
```

### 6.3 合格率统计

```
GET /api/v1/statistics/qualification-rate/

参数：
- category: 检测类别
- period: 统计周期

响应：
{
  "concrete": {
    "total": 100,
    "qualified": 95,
    "rate": 95.0
  },
  "steel": {
    "total": 80,
    "qualified": 78,
    "rate": 97.5
  }
}
```

### 6.4 强度曲线

```
GET /api/v1/statistics/strength-curve/

参数：
- sample_type: 样品类型
- project: 项目ID

响应：
{
  "ages": [3, 7, 28, 60],
  "strengths": [15.2, 25.8, 35.6, 42.1]
}
```

### 6.5 工作量统计

```
GET /api/v1/statistics/workload/

参数：
- period: month/quarter/year
- department: 部门

响应：
{
  "users": [
    {
      "name": "张三",
      "test_count": 50,
      "report_count": 40,
      "work_hours": 160
    }
  ]
}
```

### 6.6 设备使用率

```
GET /api/v1/statistics/equipment-usage/

参数：
- period: month/quarter/year
- equipment: 设备ID

响应：
{
  "equipment_name": "万能试验机",
  "usage_hours": 120,
  "usage_rate": 75.0,
  "test_count": 200
}
```

---

## 七、错误处理

### 7.1 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 验证失败 |
| 500 | 服务器错误 |

### 7.2 错误响应

```
{
  "detail": "错误详情",
  "code": "error_code",
  "field": "出错的字段"
}
```

---

*文档版本: v1.0.0*