import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/monitoring')({
  component: () => <ComingSoonPage title="Real-time Monitoring" />,
})
