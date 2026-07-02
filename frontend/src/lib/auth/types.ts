export type Role = 'super_admin' | 'org_admin' | 'member'

export interface AuthUser {
  id: number
  email: string
  full_name: string | null
  role: Role
  org: { id: number; name: string } | null
  must_change_password: boolean
}
