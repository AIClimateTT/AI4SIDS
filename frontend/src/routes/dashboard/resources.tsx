import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/resources')({
  component: () => <ComingSoonPage title="Resources & Guidance" />,
})
