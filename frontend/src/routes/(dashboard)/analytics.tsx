import { createFileRoute } from '@tanstack/react-router'
import DataAnalytics from '@/components/DataAnalytics'

export const Route = createFileRoute('/(dashboard)/analytics')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <main className="flex-1">
      <DataAnalytics />
    </main>
  )
}
