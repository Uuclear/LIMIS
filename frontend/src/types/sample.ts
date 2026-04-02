export interface Sample {
  id: number
  sample_no: string
  name: string
  specification: string
  grade: string
  quantity: number
  unit: string
  status: string
  sampling_date: string
  received_date: string
  commission_id: number
  commission_no: string
  project_name: string
  retention_deadline: string | null
  disposal_date: string | null
  created_at: string
  updated_at: string
}

export interface SampleGroup {
  id: number
  name: string
  samples: Sample[]
}

export interface SampleDisposal {
  id: number
  sample_id: number
  disposal_method: string
  disposal_date: string
  operator: string
  remark: string
}
