import { useState } from 'react'
import { ShieldAlert } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { useAuth } from '@/lib/auth/AuthContext'
import type { Org } from '@/lib/api/orgs.types'
import { OrgTable } from './components/OrgTable'
import { OrgUsersPanel } from './components/OrgUsersPanel'

export function OrgManagementPage() {
  const { user, isLoading } = useAuth()
  const [selectedOrg, setSelectedOrg] = useState<Org | null>(null)

  if (isLoading) return null

  if (!user || user.role === 'member') {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="flex items-center gap-3 p-6 text-muted-foreground">
            <ShieldAlert className="h-5 w-5" />
            You are not authorized to manage organizations.
          </CardContent>
        </Card>
      </div>
    )
  }

  if (user.role === 'org_admin') {
    if (!user.org) return null
    return (
      <div className="space-y-6 p-6">
        <OrgUsersPanel orgId={user.org.id} orgName={user.org.name} />
      </div>
    )
  }

  // super_admin
  return (
    <div className="space-y-8 p-6">
      <OrgTable onManageUsers={setSelectedOrg} />
      {selectedOrg ? (
        <OrgUsersPanel orgId={selectedOrg.id} orgName={selectedOrg.name} />
      ) : null}
    </div>
  )
}
