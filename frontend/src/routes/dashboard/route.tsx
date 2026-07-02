import { createFileRoute, redirect } from '@tanstack/react-router'
import { GovLayout } from '@/features/shell/components/GovLayout'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ location }) => {
    if (!localStorage.getItem('ai4sids_token')) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
  },
  component: GovLayout,
})
