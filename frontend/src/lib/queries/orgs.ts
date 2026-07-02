import { queryOptions, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { mutationOptions } from '@/lib/queries/tanstack-helpers'
import {
  createOrg,
  createOrgUser,
  getOrgs,
  getOrgUsers,
  resetOrgUserPassword,
  updateOrg,
  updateOrgUser,
} from '@/lib/api/orgs'
import type {
  OrgCreateInput,
  OrgUpdateInput,
  OrgUserCreateInput,
  OrgUserUpdateInput,
} from '@/lib/api/orgs.types'

// ---------------------------------------------------------------------------
// Key Factory
// ---------------------------------------------------------------------------

export const orgKeys = {
  all: () => ['orgs'] as const,
  lists: () => [...orgKeys.all(), 'list'] as const,
  list: () => [...orgKeys.lists()] as const,
  users: (orgId: number) => [...orgKeys.all(), 'users', orgId] as const,
}

// ---------------------------------------------------------------------------
// Query Options
// ---------------------------------------------------------------------------

export const orgQueries = {
  list: () =>
    queryOptions({
      queryKey: orgKeys.list(),
      queryFn: getOrgs,
    }),
  users: (orgId: number) =>
    queryOptions({
      queryKey: orgKeys.users(orgId),
      queryFn: () => getOrgUsers(orgId),
      enabled: !!orgId,
    }),
}

// ---------------------------------------------------------------------------
// Mutation Options
// ---------------------------------------------------------------------------

export const orgMutations = {
  create: () =>
    mutationOptions({
      mutationFn: (data: OrgCreateInput) => createOrg(data),
    }),
  update: () =>
    mutationOptions({
      mutationFn: ({ id, data }: { id: number; data: OrgUpdateInput }) =>
        updateOrg(id, data),
    }),
  createUser: () =>
    mutationOptions({
      mutationFn: ({ orgId, data }: { orgId: number; data: OrgUserCreateInput }) =>
        createOrgUser(orgId, data),
    }),
  updateUser: () =>
    mutationOptions({
      mutationFn: ({
        orgId,
        userId,
        data,
      }: {
        orgId: number
        userId: number
        data: OrgUserUpdateInput
      }) => updateOrgUser(orgId, userId, data),
    }),
  resetUserPassword: () =>
    mutationOptions({
      mutationFn: ({ orgId, userId }: { orgId: number; userId: number }) =>
        resetOrgUserPassword(orgId, userId),
    }),
}

// ---------------------------------------------------------------------------
// Hook Wrappers
// ---------------------------------------------------------------------------

export function useCreateOrg(onSuccess?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    ...orgMutations.create(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orgKeys.lists() })
      toast.success('Organization created')
      onSuccess?.()
    },
    onError: (error: Error) =>
      toast.error('Failed to create organization', { description: error.message }),
  })
}

export function useUpdateOrg(onSuccess?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    ...orgMutations.update(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orgKeys.lists() })
      toast.success('Organization updated')
      onSuccess?.()
    },
    onError: (error: Error) =>
      toast.error('Failed to update organization', { description: error.message }),
  })
}

export function useCreateOrgUser(orgId: number, onSuccess?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    ...orgMutations.createUser(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orgKeys.users(orgId) })
      queryClient.invalidateQueries({ queryKey: orgKeys.lists() })
      toast.success('User created')
      onSuccess?.()
    },
    onError: (error: Error) =>
      toast.error('Failed to create user', { description: error.message }),
  })
}

export function useUpdateOrgUser(orgId: number, onSuccess?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    ...orgMutations.updateUser(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orgKeys.users(orgId) })
      toast.success('User updated')
      onSuccess?.()
    },
    onError: (error: Error) =>
      toast.error('Failed to update user', { description: error.message }),
  })
}

export function useResetOrgUserPassword(orgId: number, onSuccess?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    ...orgMutations.resetUserPassword(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orgKeys.users(orgId) })
      toast.success('Password reset')
      onSuccess?.()
    },
    onError: (error: Error) =>
      toast.error('Failed to reset password', { description: error.message }),
  })
}
