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
  id_card: string
  organization: string
  certificate_no: string
}
