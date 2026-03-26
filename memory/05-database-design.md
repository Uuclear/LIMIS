# 数据库设计要点

## 数据库选型：PostgreSQL 16

选择PostgreSQL的关键原因：
- JSONB 类型支持动态表单（原始记录模板引擎）
- 全文搜索支持
- 强事务支持
- 企业级可靠性

## 核心实体关系

```
Project 1──N Commission 1──N Sample N──1 SampleGroup
                  │                    │
                  │                    ↓
                  │              TestTask 1──1 OriginalRecord
                  │                    │            │
                  │                    ↓            ↓
                  │              TestResult    RecordRevision
                  │                    │
                  ↓                    ↓
            ContractReview         Report 1──N ReportApproval
                                       │
                                       ↓
                                  ReportDistribution

Equipment 1──N Calibration
          1──N PeriodCheck
          1──N Maintenance
          1──N EquipUsageLog

Staff(User) 1──N Certificate
            1──N Authorization
            1──N Training
            1──N CompetencyEval

MonitoringPoint 1──N EnvRecord
Standard 1──N MethodValidation
Consumable 1──N ConsumableIn/Out
```

## 公共基类字段

所有业务表继承 BaseModel，包含：
- `id`: BigAutoField 主键
- `created_at`: DateTimeField 创建时间
- `updated_at`: DateTimeField 更新时间
- `created_by`: ForeignKey(User) 创建人
- `is_deleted`: BooleanField 软删除标记

## 关键Model字段设计

### Project（工程项目）
- name: 工程名称
- code: 项目编号
- address: 工程地点
- project_type: 工程类型（房建/市政/交通/水利等）
- status: 状态（进行中/已竣工/已暂停）
- start_date: 开工日期
- end_date: 计划竣工日期
- description: 备注

### Commission（委托单）
- commission_no: 委托编号（自动生成）
- project: FK(Project)
- construction_part: 施工部位
- commission_date: 委托日期
- client_unit: 委托单位名称
- witness: FK(Witness) 见证人
- is_witnessed: 是否见证取样
- status: 状态（draft/pending_review/reviewed/rejected/cancelled）
- reviewer: FK(User) 评审人
- review_date: 评审日期
- review_comment: 评审意见

### Sample（样品）
- sample_no: 样品编号（自动生成）
- blind_no: 盲样编号
- commission: FK(Commission)
- name: 样品名称
- specification: 规格型号
- grade: 设计强度等级/技术要求
- quantity: 数量
- unit: 单位
- sampling_date: 取样日期
- received_date: 收样日期
- production_date: 生产/成型日期
- sampling_location: 取样地点
- status: 状态（pending/testing/tested/retained/disposed/returned）
- group: FK(SampleGroup, null)
- retention_deadline: 留样到期日
- disposal_date: 处置日期
- disposal_method: 处置方式

### TestTask（检测任务）
- task_no: 任务编号
- sample: FK(Sample)
- commission: FK(Commission)
- test_project: FK(TestProject) 检测项目
- test_method: FK(TestMethod) 检测方法
- assigned_tester: FK(User) 检测员
- assigned_equipment: FK(Equipment) 设备
- planned_date: 计划检测日期（龄期到期日）
- actual_date: 实际检测日期
- status: 状态
- age_days: 龄期天数（如28）

### OriginalRecord（原始记录）
- task: OneToOne(TestTask)
- template: FK(RecordTemplate) 模板
- template_version: 模板版本号
- record_data: JSONField 记录数据
- env_temperature: 环境温度
- env_humidity: 环境湿度
- status: 状态（draft/pending_review/reviewed/returned）
- recorder: FK(User) 记录人
- reviewer: FK(User) 复核人
- review_date: 复核日期
- review_comment: 复核意见
- signature_recorder: 记录人电子签名
- signature_reviewer: 复核人电子签名

### TestResult（检测结果）
- task: FK(TestTask)
- parameter: FK(TestParameter) 检测参数
- raw_value: 原始值
- rounded_value: 修约后值
- unit: 单位
- judgment: 判定结论（qualified/unqualified/NA）
- standard_value: 标准限值
- design_value: 设计值
- remark: 备注

### Report（检测报告）
- report_no: 报告编号
- commission: FK(Commission)
- template: 报告模板路径
- status: 状态
- compiler: FK(User) 编制人
- compile_date: 编制日期
- auditor: FK(User) 审核人
- audit_date: 审核日期
- approver: FK(User) 批准人（授权签字人）
- approve_date: 批准日期
- issue_date: 发放日期
- pdf_file: 报告PDF文件路径
- qr_code: 防伪二维码
- has_cma: 是否带CMA标识
- conclusion: 检测结论

### Equipment（仪器设备）
- name: 设备名称
- model: 型号
- serial_no: 出厂编号
- manage_no: 管理编号
- manufacturer: 制造商
- category: 分类（A/B/C）
- accuracy: 精度/分辨力
- measure_range: 量程
- purchase_date: 购入日期
- status: 状态（in_use/stopped/calibrating/scrapped）
- location: 存放位置
- calibration_cycle: 检定/校准周期（月）
- next_calibration_date: 下次校准到期日

## 索引策略

为常用查询字段建立索引：
- Commission: commission_no, project_id, status, commission_date
- Sample: sample_no, blind_no, commission_id, status, sampling_date
- TestTask: task_no, sample_id, status, planned_date, assigned_tester_id
- Report: report_no, commission_id, status, approve_date
- Equipment: manage_no, status, next_calibration_date

## JSON动态表单存储

原始记录使用 PostgreSQL JSONB 存储，格式示例：
```json
{
  "specimen_dimensions": [
    {"length": 150.0, "width": 150.0, "height": 150.0}
  ],
  "test_data": [
    {"specimen_no": 1, "load_kn": 852.3, "area_mm2": 22500},
    {"specimen_no": 2, "load_kn": 876.1, "area_mm2": 22500},
    {"specimen_no": 3, "load_kn": 841.7, "area_mm2": 22500}
  ],
  "calculated_results": {
    "individual_strengths": [37.9, 38.9, 37.4],
    "average_strength": 38.1,
    "size_correction_factor": 0.95,
    "corrected_strength": 36.2
  }
}
```
