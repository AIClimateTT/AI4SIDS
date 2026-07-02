export type AssignableRole = 'org_admin' | 'member'

export interface Org {
  id: number
  name: string
  description: string | null
  is_active: boolean
  created_at: string | null
  user_count: number
}

export interface OrgUser {
  id: number
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  must_change_password: boolean
  created_at: string | null
}

export interface OrgUserCreated extends OrgUser {
  temp_password: string
}

export interface OrgCreateInput {
  name: string
  description?: string
}

export interface OrgUpdateInput {
  name?: string
  description?: string
  is_active?: boolean
}

export interface OrgUserCreateInput {
  email: string
  full_name?: string
  role: AssignableRole
}

export interface OrgUserUpdateInput {
  role?: AssignableRole
  is_active?: boolean
}
