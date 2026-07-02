import { createFileRoute, redirect } from '@tanstack/react-router'
import { ChangePasswordPage } from '@/features/auth/ChangePasswordPage'

export const Route = createFileRoute('/change-password')({
  beforeLoad: () => {
    if (!localStorage.getItem('ai4sids_token')) {
      throw redirect({ to: '/login', search: { redirect: '/dashboard' } })
    }
  },
  component: ChangePasswordPage,
})
