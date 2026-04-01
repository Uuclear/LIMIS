export interface Project {
  id: number
  project_no: string
  name: string
  type: string
  status: string
  address: string
  start_date: string
  end_date: string
  description: string
  created_at: string
  updated_at: string
}

export interface Organization {
  id: number
  project_id: number
  name: string
  type: string
  contact_person: string
  contact_phone: string
  qualification: string
}

export interface SubProject {
  id: number
  project_id: number
  parent_id: number | null
  name: string
  code: string
  description: string
  children?: SubProject[]
}

export interface Contract {
  id: number
  project_id: number
  contract_no: string
  name: string
  amount: number
  sign_date: string
  start_date: string
  end_date: string
  status: string
}

export interface Witness {
  id: number
  project_id: number
  name: string
  phone: string
  /** 证件号（后端字段 id_number） */
  id_number?: string
  id_type?: string
  id_type_display?: string
  organization?: number | null
  certificate_no: string
}

export interface Sampler {
  id: number
  project_id: number
  name: string
  phone: string
  id_number?: string
  id_type?: string
  id_type_display?: string
  organization?: number | null
  certificate_no: string
}
