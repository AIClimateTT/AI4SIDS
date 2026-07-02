import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { ReactNode } from 'react'
import { OrgUsersPanel } from '../components/OrgUsersPanel'

vi.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 1,
      email: 'admin@a.org',
      full_name: 'Admin A',
      role: 'org_admin',
      org: { id: 5, name: 'Ministry of Environment' },
      must_change_password: false,
    },
    isLoading: false,
  }),
}))

const USERS = [
  {
    id: 1,
    email: 'admin@a.org',
    full_name: 'Admin A',
    role: 'org_admin',
    is_active: true,
    must_change_password: false,
    created_at: null,
  },
  {
    id: 2,
    email: 'member@a.org',
    full_name: null,
    role: 'member',
    is_active: true,
    must_change_password: false,
    created_at: null,
  },
]

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

function mockFetch() {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.includes('/api/orgs/5/users') && (!init || !init.method)) {
      return new Response(JSON.stringify(USERS), { status: 200 })
    }
    if (url.includes('/api/orgs/5/users') && init?.method === 'POST') {
      return new Response(
        JSON.stringify({
          id: 3,
          email: 'new@a.org',
          full_name: null,
          role: 'member',
          is_active: true,
          must_change_password: true,
          created_at: null,
          temp_password: 'tmp-secret-42',
        }),
        { status: 201 },
      )
    }
    throw new Error(`Unexpected fetch: ${init?.method ?? 'GET'} ${url}`)
  })
}

describe('OrgUsersPanel', () => {
  it('lists the org users', async () => {
    vi.stubGlobal('fetch', mockFetch())
    render(<OrgUsersPanel orgId={5} orgName="Ministry of Environment" />, { wrapper })
    expect(await screen.findByText('admin@a.org')).toBeInTheDocument()
    expect(screen.getByText('member@a.org')).toBeInTheDocument()
  })

  it('add-user flow shows the temp password exactly once', async () => {
    vi.stubGlobal('fetch', mockFetch())
    render(<OrgUsersPanel orgId={5} orgName="Ministry of Environment" />, { wrapper })
    await screen.findByText('admin@a.org')

    fireEvent.click(screen.getByRole('button', { name: /add user/i }))
    fireEvent.change(await screen.findByLabelText(/email/i), {
      target: { value: 'new@a.org' },
    })
    fireEvent.click(screen.getByRole('button', { name: /create user/i }))

    const shown = await screen.findByTestId('temp-password')
    expect(shown.textContent).toBe('tmp-secret-42')

    fireEvent.click(screen.getByRole('button', { name: /done/i }))
    await waitFor(() =>
      expect(screen.queryByTestId('temp-password')).not.toBeInTheDocument(),
    )
  })
})
