export interface Commission {
  id: number
  commission_no: string
  project: number
  project_name: string
  sub_project: number | null
  sub_project_name: string
  construction_part: string
  commission_date: string
  client_unit: string
  client_contact?: string
  client_phone: string
  witness: number | null
  witness_name: string
  is_witnessed: boolean
  status: string
  status_display?: string
  items: CommissionItem[]
  contract_review: ContractReview | null
  created_at: string
  updated_at: string
}

export interface CommissionItem {
  id?: number
  commission?: number
  test_object: string
  test_item: string
  test_standard: string
  test_method?: string
  specification: string
  grade: string
  quantity: number
  unit: string
  remark?: string
}

/** 与后端 ContractReview 一致 */
export interface ContractReview {
  id: number
  commission: number
  has_capability: boolean
  has_equipment: boolean
  has_personnel: boolean
  method_valid: boolean
  sample_representative: boolean
  conclusion: 'accept' | 'reject' | 'conditional' | string
  reviewer: number | null
  reviewer_name: string
  review_date: string | null
  comment: string
}
