import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/assistant')({
  component: () => <ComingSoonPage title="AI Preparedness Assistant" />,
})
