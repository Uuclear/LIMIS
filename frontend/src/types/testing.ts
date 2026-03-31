export interface TestCategory {
  id: number
  name: string
  code: string
  parent_id: number | null
  sort_order: number
  is_active: boolean
}

export interface TestMethod {
  id: number
  name: string
  code: string
  standard_no: string
  standard_name: string
  category_id: number
  category_name: string
  is_active: boolean
}

export interface TestParameter {
  id: number
  name: string
  code: string
  unit: string
  method_id: number
  method_name: string
  decimal_places: number
  default_limit_low: number | null
  default_limit_high: number | null
  remark: string
}

export interface TestTask {
  id: number
  task_no: string
  status: 'unassigned' | 'assigned' | 'in_progress' | 'completed' | 'abnormal'
  sample_id: number
  sample_no: string
  sample_name: string
  commission_id: number
  commission_no: string
  method_id: number
  method_name: string
  standard_no: string
  parameters: TestParameter[]
  tester_id: number | null
  tester_name: string
  planned_date: string
  started_at: string | null
  completed_at: string | null
  equipment_ids: number[]
  equipment_names: string[]
  remark: string
  created_at: string
  updated_at: string
}

export interface RecordTemplate {
  id: number
  name: string
  code: string
  method_id: number
  method_name: string
  schema: Record<string, any>
  version: string
  is_active: boolean
  created_at: string
}

export interface OriginalRecord {
  id: number
  record_no: string
  task_id: number
  task_no: string
  template_id: number
  template_name: string
  recorder_id: number
  recorder_name: string
  status: 'draft' | 'pending_review' | 'reviewed' | 'returned'
  data: Record<string, any>
  environment_temp: number | null
  environment_humidity: number | null
  equipment_ids: number[]
  equipment_names: string[]
  reviewer_id: number | null
  reviewer_name: string
  review_date: string | null
  review_comment: string
  created_at: string
  updated_at: string
}

export interface TestResult {
  id: number
  task_id: number
  task_no: string
  parameter_id: number
  parameter_name: string
  unit: string
  value: string
  numeric_value: number | null
  limit_low: number | null
  limit_high: number | null
  is_qualified: boolean | null
  judgment: string
  remark: string
  created_at: string
}

export interface JudgmentRule {
  id: number
  parameter_id: number
  rule_type: 'range' | 'threshold' | 'enum'
  condition: string
  limit_low: number | null
  limit_high: number | null
  allowed_values: string[]
  result_text: string
}
