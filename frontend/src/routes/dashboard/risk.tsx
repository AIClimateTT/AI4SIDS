import { createFileRoute } from '@tanstack/react-router'
import { RiskPage } from '@/features/risk/RiskPage'

export const Route = createFileRoute('/dashboard/risk')({
  component: RiskPage,
})
