import { useEffect, type ReactNode } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useAuth } from '@/lib/auth/AuthContext'

/** Redirects users flagged must_change_password to the change-password
 * screen. Renders nothing while the user profile is still loading so
 * flagged users never see a flash of dashboard content. */
export function RequirePasswordFresh({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && user?.must_change_password) {
      void navigate({ to: '/change-password' })
    }
  }, [isLoading, user, navigate])

  if (isLoading || user?.must_change_password) return null
  return children
}
