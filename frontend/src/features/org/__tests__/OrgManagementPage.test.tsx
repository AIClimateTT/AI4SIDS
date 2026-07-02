import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { ReactNode } from 'react'

const mockUseAuth = vi.fn()
vi.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => mockUseAuth(),
}))

import { OrgManagementPage } from '../OrgManagementPage'

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

function authAs(role: string, org: { id: number; name: string } | null) {
  mockUseAuth.mockReturnValue({
    user: {
      id: 1,
      email: 'u@x.org',
      full_name: null,
      role,
      org,
      must_change_password: false,
    },
    isLoading: false,
  })
}

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => new Response(JSON.stringify([]), { status: 200 })),
  )
})

describe('OrgManagementPage role switch', () => {
  it('member sees not-authorized', () => {
    authAs('member', { id: 5, name: 'Met Office' })
    render(<OrgManagementPage />, { wrapper })
    expect(screen.getByText(/not authorized/i)).toBeInTheDocument()
  })

  it('org_admin lands on their own user panel', async () => {
    authAs('org_admin', { id: 5, name: 'Met Office' })
    render(<OrgManagementPage />, { wrapper })
    expect(await screen.findByText('Met Office — Users')).toBeInTheDocument()
    expect(screen.queryByText('Organizations')).not.toBeInTheDocument()
  })

  it('super_admin sees the org table', async () => {
    authAs('super_admin', null)
    render(<OrgManagementPage />, { wrapper })
    expect(await screen.findByText('Organizations')).toBeInTheDocument()
  })
})
