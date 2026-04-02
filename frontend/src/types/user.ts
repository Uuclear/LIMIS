export interface UserInfo {
  id: number
  username: string
  real_name: string
  first_name: string
  last_name: string
  email: string
  phone: string
  avatar: string
  department: string
  title: string
  roles: Role[]
  permissions: string[]
  is_active: boolean
  last_login: string
  date_joined: string
}

export interface Role {
  id: number
  name: string
  code: string
  description: string
}

export interface Permission {
  id: number
  name: string
  code: string
  type: string
}

export interface LoginForm {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: UserInfo
}
