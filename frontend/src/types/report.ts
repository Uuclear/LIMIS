export interface Report {
  id: number
  report_no: string
  title: string
  status: 'draft' | 'pending_audit' | 'pending_approve' | 'approved' | 'issued' | 'voided'
  commission_id: number
  commission_no: string
  project_name: string
  client_name: string
  sample_ids: number[]
  sample_names: string[]
  compiler_id: number
  compiler_name: string
  compile_date: string
  has_cma: boolean
  has_cnas: boolean
  pdf_url: string | null
  conclusion: string
  remark: string
  issued_at: string | null
  voided_at: string | null
  void_reason: string
  created_at: string
  updated_at: string
  approvals: ReportApproval[]
  distributions: ReportDistribution[]
}

export interface ReportApproval {
  id: number
  report_id?: number
  report?: number
  step?: 'audit' | 'approve'
  role?: 'compile' | 'audit' | 'approve'
  action: 'approve' | 'reject' | 'pass'
  operator_id?: number
  operator_name?: string
  user?: number
  user_name?: string
  comment: string
  signature_url?: string | null
  signature?: string | null
  created_at: string
}

export interface ReportDistribution {
  id: number
  report_id: number
  recipient: string
  method: 'email' | 'print' | 'pickup'
  distributed_at: string
  operator_id: number
  operator_name: string
  remark: string
}
