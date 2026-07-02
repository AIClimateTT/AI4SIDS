import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ChangePasswordForm } from '../ChangePasswordPage'

describe('ChangePasswordForm', () => {
  it('submits current and new password with the bearer token', async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify({ status: 'password_changed' }), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const onSuccess = vi.fn()

    render(<ChangePasswordForm token="tok-9" onSuccess={onSuccess} />)
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'temp1234' },
    })
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'brand-new-pw-9' },
    })
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'brand-new-pw-9' },
    })
    fireEvent.click(screen.getByRole('button', { name: /update password/i }))

    await waitFor(() => expect(onSuccess).toHaveBeenCalled())
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    expect(String(url)).toContain('/auth/change-password')
    expect(init.headers).toMatchObject({
      Authorization: 'Bearer tok-9',
    })
    expect(JSON.parse(init.body as string)).toEqual({
      current_password: 'temp1234',
      new_password: 'brand-new-pw-9',
    })
  })

  it('blocks mismatched confirmation without calling the API', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    render(<ChangePasswordForm token="tok-9" onSuccess={vi.fn()} />)
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'temp1234' },
    })
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'one-password-1' },
    })
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'different-2' },
    })
    fireEvent.click(screen.getByRole('button', { name: /update password/i }))

    expect(await screen.findByText(/do not match/i)).toBeDefined()
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
