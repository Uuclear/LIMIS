# API接口设计规范

## URL规范

- 基础路径：`/api/v1/`
- 资源命名：复数名词，kebab-case
- 嵌套不超过2层

## 接口清单（按模块）

### 认证（/api/v1/auth/）
```
POST   /auth/login/            登录（返回JWT Token）
POST   /auth/logout/           登出
POST   /auth/token/refresh/    刷新Token
GET    /auth/me/               当前用户信息
PUT    /auth/password/         修改密码
```

### 系统管理（/api/v1/system/）
```
GET/POST       /system/users/              用户列表/创建
GET/PUT/DELETE /system/users/{id}/         用户详情/修改/删除
GET/POST       /system/roles/              角色列表/创建
GET/PUT/DELETE /system/roles/{id}/         角色详情/修改/删除
GET/POST       /system/permissions/        权限列表/创建
GET            /system/audit-logs/         操作日志列表
GET            /system/dictionaries/       字典数据
```

### 工程项目（/api/v1/projects/）
```
GET/POST       /projects/                  项目列表/创建
GET/PUT/DELETE /projects/{id}/             项目详情/修改/删除
GET/POST       /projects/{id}/organizations/  参建单位
GET/POST       /projects/{id}/sub-projects/   分部分项工程
GET/POST       /projects/{id}/contracts/      检测合同
GET/POST       /projects/{id}/witnesses/      见证人
GET            /projects/{id}/stats/          项目统计
```

### 委托管理（/api/v1/commissions/）
```
GET/POST       /commissions/               委托列表/创建
GET/PUT/DELETE /commissions/{id}/          委托详情/修改/删除
POST           /commissions/{id}/submit/   提交评审
POST           /commissions/{id}/review/   合同评审（通过/退回）
GET/POST       /commissions/{id}/items/    委托检测项目明细
GET            /commissions/{id}/print/    打印数据
```

### 样品管理（/api/v1/samples/）
```
GET/POST       /samples/                   样品列表/创建（支持批量）
GET/PUT        /samples/{id}/              样品详情/修改
POST           /samples/{id}/status/       状态变更
GET            /samples/{id}/timeline/     流转时间线
GET            /samples/{id}/label/        标签数据（含二维码）
POST           /samples/batch-register/    批量登记
GET            /samples/retention/         留样列表（含到期提醒）
POST           /samples/{id}/dispose/      处置
GET            /samples/export/            台账导出
```

### 检测任务（/api/v1/test-tasks/）
```
GET/POST       /test-tasks/                任务列表/创建
GET/PUT        /test-tasks/{id}/           任务详情/修改
POST           /test-tasks/{id}/assign/    分配任务
POST           /test-tasks/{id}/start/     开始检测
POST           /test-tasks/{id}/complete/  完成检测
GET            /test-tasks/today/          今日待检
GET            /test-tasks/overdue/        超期任务
GET            /test-tasks/age-calendar/   龄期日历数据
```

### 原始记录（/api/v1/records/）
```
GET/POST       /records/                   记录列表/创建
GET/PUT        /records/{id}/              记录详情/修改
POST           /records/{id}/submit/       提交复核
POST           /records/{id}/review/       复核（通过/退回）
GET            /records/{id}/revisions/    修改历史
GET            /records/templates/         记录模板列表
GET            /records/templates/{id}/    模板定义详情
```

### 检测结果（/api/v1/test-results/）
```
GET/POST       /test-results/              结果列表/保存
GET            /test-results/{id}/         结果详情
POST           /test-results/calculate/    触发计算
GET            /test-results/unqualified/  不合格结果列表
```

### 报告管理（/api/v1/reports/）
```
GET/POST       /reports/                   报告列表/创建
GET/PUT        /reports/{id}/              报告详情/修改
POST           /reports/{id}/generate/     生成报告（PDF）
POST           /reports/{id}/submit-audit/ 提交审核
POST           /reports/{id}/audit/        审核（通过/退回）
POST           /reports/{id}/approve/      批准（通过/退回）
POST           /reports/{id}/issue/        发放
POST           /reports/{id}/void/         作废
GET            /reports/{id}/preview/      预览（PDF）
GET            /reports/{id}/download/     下载
POST           /reports/{id}/distribute/   发放登记
GET            /reports/verify/{qr_code}/  验真（公开接口）
```

### 仪器设备（/api/v1/equipment/）
```
GET/POST       /equipment/                 设备列表/创建
GET/PUT        /equipment/{id}/            设备详情/修改
GET/POST       /equipment/{id}/calibrations/   校准记录
GET/POST       /equipment/{id}/period-checks/  期间核查
GET/POST       /equipment/{id}/maintenances/   维保记录
GET            /equipment/{id}/usage-logs/     使用记录
GET            /equipment/expiring/            即将到期设备
GET            /equipment/{id}/traceability/   量值溯源链
```

### 人员管理（/api/v1/staff/）
```
GET/POST       /staff/                     人员列表/创建
GET/PUT        /staff/{id}/                人员详情/修改
GET/POST       /staff/{id}/certificates/   资质证书
GET/POST       /staff/{id}/authorizations/ 授权记录
GET/POST       /staff/{id}/trainings/      培训记录
GET/POST       /staff/{id}/evaluations/    能力评价
GET            /staff/expiring-certs/      证书即将到期
```

### 环境监控（/api/v1/environment/）
```
GET/POST       /environment/points/        监控点位
GET            /environment/realtime/      实时数据
POST           /environment/data/          数据上报（传感器调用）
GET            /environment/history/       历史数据
GET            /environment/alarms/        报警记录
```

### 标准管理（/api/v1/standards/）
```
GET/POST       /standards/                 标准列表/创建
GET/PUT        /standards/{id}/            标准详情/修改
GET            /standards/expiring/        即将废止标准
GET/POST       /standards/{id}/validations/ 方法验证记录
```

### 质量管理（/api/v1/quality/）
```
GET/POST       /quality/audits/            内部审核
GET/POST       /quality/audits/{id}/findings/ 审核发现
GET/POST       /quality/reviews/           管理评审
GET/POST       /quality/nonconformities/   不符合项
GET/POST       /quality/complaints/        投诉处理
GET/POST       /quality/proficiency-tests/ 能力验证
GET/POST       /quality/supervisions/      质量监督
```

### 耗材管理（/api/v1/consumables/）
```
GET/POST       /consumables/               耗材列表/创建
GET/PUT        /consumables/{id}/          耗材详情/修改
POST           /consumables/{id}/in/       入库
POST           /consumables/{id}/out/      出库/领用
GET            /consumables/low-stock/     库存预警
GET            /consumables/expiring/      即将过期
```

### 统计分析（/api/v1/statistics/）
```
GET   /statistics/dashboard/       看板数据（关键指标汇总）
GET   /statistics/test-volume/     检测量统计
GET   /statistics/qualification/   合格率统计
GET   /statistics/strength-curve/  强度发展曲线
GET   /statistics/cycle-analysis/  检测周期分析
GET   /statistics/workload/        人员工作量
GET   /statistics/equipment-usage/ 设备利用率
GET   /statistics/export/          报表导出
```

## 统一响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 分页响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 150,
    "page": 1,
    "page_size": 20,
    "results": [ ... ]
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": {
    "field_name": ["错误描述"]
  }
}
```

## 认证方式

- JWT Bearer Token
- Header: `Authorization: Bearer <access_token>`
- Access Token 有效期：2小时
- Refresh Token 有效期：7天
