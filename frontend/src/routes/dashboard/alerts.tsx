import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/alerts')({
  component: () => <ComingSoonPage title="Alerts & Notifications" />,
})
