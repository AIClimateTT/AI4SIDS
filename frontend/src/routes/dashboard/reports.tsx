import { createFileRoute } from '@tanstack/react-router'
import { ReportsPage } from '@/features/reports/ReportsPage'

export const Route = createFileRoute('/dashboard/reports')({
  component: ReportsPage,
})
