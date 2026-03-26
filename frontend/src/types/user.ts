export interface UserInfo {
  id: number
  username: string
  realName: string
  email: string
  phone: string
  avatar: string
  department: string
  roles: Role[]
  permissions: string[]
  isActive: boolean
  lastLogin: string
  createdAt: string
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
