import { createFileRoute, redirect } from '@tanstack/react-router'
import { GovLayout } from '@/features/shell/components/GovLayout'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: () => {
    const token = localStorage.getItem('ai4sids_token')
    if (!token) {
      throw redirect({ to: '/' })
    }
  },
  component: GovLayout,
})
