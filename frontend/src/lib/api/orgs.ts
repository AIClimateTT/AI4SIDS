import { http } from './http'
import type {
  Org,
  OrgCreateInput,
  OrgUpdateInput,
  OrgUser,
  OrgUserCreateInput,
  OrgUserCreated,
  OrgUserUpdateInput,
} from './orgs.types'

export async function getOrgs(): Promise<Org[]> {
  return http<Org[]>('/api/orgs')
}

export async function createOrg(payload: OrgCreateInput): Promise<Org> {
  return http<Org>('/api/orgs', { method: 'POST', body: JSON.stringify(payload) })
}

export async function updateOrg(id: number, payload: OrgUpdateInput): Promise<Org> {
  return http<Org>(`/api/orgs/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function getOrgUsers(orgId: number): Promise<OrgUser[]> {
  return http<OrgUser[]>(`/api/orgs/${orgId}/users`)
}

export async function createOrgUser(
  orgId: number,
  payload: OrgUserCreateInput,
): Promise<OrgUserCreated> {
  return http<OrgUserCreated>(`/api/orgs/${orgId}/users`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateOrgUser(
  orgId: number,
  userId: number,
  payload: OrgUserUpdateInput,
): Promise<OrgUser> {
  return http<OrgUser>(`/api/orgs/${orgId}/users/${userId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function resetOrgUserPassword(
  orgId: number,
  userId: number,
): Promise<{ temp_password: string }> {
  return http<{ temp_password: string }>(
    `/api/orgs/${orgId}/users/${userId}/reset-password`,
    { method: 'POST' },
  )
}
