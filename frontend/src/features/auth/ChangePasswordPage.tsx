import { useState, type FormEvent } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useAuth } from '@/lib/auth/AuthContext'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ''

export function ChangePasswordForm({
  token,
  onSuccess,
}: {
  token: string
  onSuccess: () => void
}) {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (next !== confirm) {
      setError('New passwords do not match')
      return
    }
    setSubmitting(true)
    try {
      const res = await fetch(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ current_password: current, new_password: next }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail ?? 'Could not change password')
      }
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not change password')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="current" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Current password
        </label>
        <input
          id="current"
          type="password"
          required
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
        />
      </div>
      <div>
        <label htmlFor="next" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          New password
        </label>
        <input
          id="next"
          type="password"
          required
          minLength={8}
          value={next}
          onChange={(e) => setNext(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
        />
      </div>
      <div>
        <label htmlFor="confirm" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Confirm new password
        </label>
        <input
          id="confirm"
          type="password"
          required
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
        />
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {submitting ? 'Updating…' : 'Update password'}
      </button>
    </form>
  )
}

export function ChangePasswordPage() {
  const { token, refreshUser } = useAuth()
  const navigate = useNavigate()

  if (!token) return null

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-xl dark:bg-slate-800">
        <h1 className="mb-1 text-lg font-bold text-slate-900 dark:text-white">
          Set a new password
        </h1>
        <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
          You must change your temporary password before continuing.
        </p>
        <ChangePasswordForm
          token={token}
          onSuccess={() => {
            void refreshUser().then(() => navigate({ to: '/dashboard' }))
          }}
        />
      </div>
    </div>
  )
}
