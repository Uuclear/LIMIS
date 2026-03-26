export interface Commission {
  id: number
  commission_no: string
  project_id: number
  project_name: string
  sub_project_id: number | null
  sub_project_name: string
  construction_part: string
  commission_date: string
  client_name: string
  client_phone: string
  witness_id: number | null
  witness_name: string
  witness_sampling: boolean
  status: string
  items: CommissionItem[]
  review: ContractReview | null
  created_at: string
  updated_at: string
}

export interface CommissionItem {
  id?: number
  commission_id?: number
  test_object: string
  test_item: string
  test_standard: string
  specification: string
  design_grade: string
  quantity: number
  unit: string
}

export interface ContractReview {
  id: number
  commission_id: number
  reviewer_id: number
  reviewer_name: string
  result: string
  opinion: string
  reviewed_at: string
}
