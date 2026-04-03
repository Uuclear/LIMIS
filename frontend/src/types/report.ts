export interface Report {
  id: number
  report_no: string
  commission: number
  commission_no: string
  report_type: string
  template_name: string
  status: 'draft' | 'pending_audit' | 'pending_approve' | 'approved' | 'issued' | 'archived' | 'voided'
  status_display: string
  compiler: number | null
  compiler_name: string
  compile_date: string | null
  auditor: number | null
  auditor_name: string
  audit_date: string | null
  approver: number | null
  approver_name: string
  approve_date: string | null
  conclusion: string
  pdf_file: string | null
  qr_code: string | null
  has_cma: boolean
  issue_date: string | null
  remark: string
  created_at: string
  updated_at: string
  created_by: number | null
  created_by_name: string
  approvals: ReportApproval[]
  distributions: ReportDistribution[]
}

export interface ReportApproval {
  id: number
  report: number
  role: 'compile' | 'audit' | 'approve'
  role_display: string
  action: 'submit' | 'pass' | 'reject'
  action_display: string
  user: number
  user_name: string
  comment: string
  signature: string | null
  created_at: string
  updated_at: string
}

export interface ReportDistribution {
  id: number
  report: number
  recipient: string
  recipient_unit: string
  method: 'email' | 'print' | 'pickup'
  method_display: string
  copies: number
  distribution_date: string
  receiver_signature: string | null
  created_at: string
  updated_at: string
}
