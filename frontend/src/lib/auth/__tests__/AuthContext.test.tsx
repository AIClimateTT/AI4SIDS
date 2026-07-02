import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider, useAuth } from '../AuthContext'
import type { ReactNode } from 'react'

const wrapper = ({ children }: { children: ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

const ME = {
  id: 1,
  email: 'oa@met.org',
  full_name: 'Org Admin',
  role: 'org_admin',
  org: { id: 2, name: 'Met Office' },
  must_change_password: false,
}

function mockFetch(routes: Record<string, { status: number; body: unknown }>) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    const match = Object.entries(routes).find(([path]) => url.includes(path))
    if (!match) throw new Error(`Unexpected fetch: ${url}`)
    const { status, body } = match[1]
    return new Response(JSON.stringify(body), { status })
  })
}

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('AuthContext', () => {
  it('login stores token and loads the user from /auth/me', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/token': { status: 200, body: { access_token: 'tok-1', token_type: 'bearer' } },
        '/auth/me': { status: 200, body: ME },
      }),
    )
    const { result } = renderHook(() => useAuth(), { wrapper })
    await act(() => result.current.login('oa@met.org', 'pw'))
    await waitFor(() => expect(result.current.user).not.toBeNull())
    expect(localStorage.getItem('ai4sids_token')).toBe('tok-1')
    expect(result.current.user?.role).toBe('org_admin')
    expect(result.current.hasRole('org_admin')).toBe(true)
    expect(result.current.hasRole('super_admin')).toBe(false)
  })

  it('super_admin passes every hasRole check', async () => {
    vi.stubGlobal(
      'fetch',
      mockFetch({
        '/auth/token': { status: 200, body: { access_token: 't', token_type: 'bearer' } },
        '/auth/me': { status: 200, body: { ...ME, role: 'super_admin', org: null } },
      }),
    )
    const { result } = renderHook(() => useAuth(), { wrapper })
    await act(() => result.current.login('root@x.org', 'pw'))
    await waitFor(() => expect(result.current.user).not.toBeNull())
    expect(result.current.hasRole('member')).toBe(true)
    expect(result.current.hasRole('org_admin')).toBe(true)
  })

  it('a 401 from /auth/me clears the session', async () => {
    localStorage.setItem('ai4sids_token', 'stale-token')
    vi.stubGlobal(
      'fetch',
      mockFetch({ '/auth/me': { status: 401, body: { detail: 'nope' } } }),
    )
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.isAuthenticated).toBe(false)
    expect(localStorage.getItem('ai4sids_token')).toBeNull()
  })
})
