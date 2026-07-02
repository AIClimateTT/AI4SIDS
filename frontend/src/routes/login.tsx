import { createFileRoute } from '@tanstack/react-router'
import { LoginPage } from '@/features/auth/LoginPage'

export const Route = createFileRoute('/login')({
  validateSearch: (search: Record<string, unknown>) => ({
    redirect: typeof search.redirect === 'string' ? search.redirect : '/dashboard',
  }),
  component: LoginPage,
})
