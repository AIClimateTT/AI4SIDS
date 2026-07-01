import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/risk')({
  component: () => <ComingSoonPage title="Risk & Vulnerability" />,
})
