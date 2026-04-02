export interface TestCategory {
  id: number
  name: string
  code: string
  parent: number | null
  sort_order: number
  children?: TestCategory[]
  created_at: string
  updated_at: string
}

export interface TestParameter {
  id: number
  category: number | null
  category_name: string
  standard: number | null
  standard_display: string
  standard_no: string
  standard_name: string
  name: string
  code: string
  unit: string
  precision: number
  min_value: number | null
  max_value: number | null
  is_required: boolean
  is_active: boolean
  description: string
  created_at: string
  updated_at: string
}

export interface TestTask {
  id: number
  task_no: string
  status: 'unassigned' | 'in_progress' | 'completed'
  status_display: string
  sample: number
  sample_no: string
  sample_name: string
  commission: number
  commission_no: string
  test_parameter: number
  parameter_name: string
  standard_no: string
  assigned_tester: number | null
  tester_name: string
  assigned_equipment: number | null
  planned_date: string
  actual_date: string | null
  age_days: number | null
  is_overdue: boolean
  started_at: string | null
  completed_at: string | null
  remark: string
  created_at: string
  updated_at: string
}

export interface RecordTemplate {
  id: number
  name: string
  code: string
  test_parameter: number | null
  parameter_name: string
  test_parameters: number[]
  parameter_names: string[]
  version: string
  schema: Record<string, any>
  word_template: string | null
  word_template_url: string | null
  template_kind: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface OriginalRecord {
  id: number
  task: number
  task_no: string
  template: number
  template_version: string
  record_data: Record<string, any>
  env_temperature: number | null
  env_humidity: number | null
  status: 'draft' | 'pending_review' | 'reviewed' | 'returned'
  status_display: string
  recorder: number
  recorder_name: string
  reviewer: number | null
  reviewer_name: string
  review_date: string | null
  review_comment: string
  revisions: RecordRevision[]
  created_at: string
  updated_at: string
}

export interface RecordRevision {
  id: number
  field_path: string
  old_value: string
  new_value: string
  changed_by: number
  changed_by_name: string
  changed_at: string
}

export interface TestResult {
  id: number
  task: number
  parameter: number
  parameter_name: string
  raw_value: string
  rounded_value: string
  display_value: string
  unit: string
  judgment: string
  judgment_display: string
  standard_value: string
  design_value: string
  remark: string
  created_at: string
  updated_at: string
}

export interface JudgmentRule {
  id: number
  test_parameter: number
  parameter_name: string
  grade: string
  min_value: number | null
  max_value: number | null
  standard_ref: string
  created_at: string
  updated_at: string
}
