import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/reports')({
  component: () => <ComingSoonPage title="Reports & Analytics" />,
})
