import { createFileRoute } from '@tanstack/react-router'
import { OrgManagementPage } from '@/features/org/OrgManagementPage'

export const Route = createFileRoute('/dashboard/org')({
  component: OrgManagementPage,
})
