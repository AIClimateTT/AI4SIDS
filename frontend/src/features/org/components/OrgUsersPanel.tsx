import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { MoreHorizontal, Plus } from 'lucide-react'
import type { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useAuth } from '@/lib/auth/AuthContext'
import {
  orgQueries,
  useResetOrgUserPassword,
  useUpdateOrgUser,
} from '@/lib/queries/orgs'
import type { OrgUser } from '@/lib/api/orgs.types'
import { TempPasswordDialog } from './TempPasswordDialog'
import { UserFormDialog } from './UserFormDialog'

const PAGE_SIZE = 10

export function OrgUsersPanel({ orgId, orgName }: { orgId: number; orgName: string }) {
  const { user: me } = useAuth()
  const { data: users, isPending, error } = useQuery(orgQueries.users(orgId))
  const [pageIndex, setPageIndex] = useState(0)
  const [addOpen, setAddOpen] = useState(false)
  const [tempPassword, setTempPassword] = useState<{ password: string; email: string } | null>(null)

  const updateUser = useUpdateOrgUser(orgId)
  const resetPassword = useResetOrgUserPassword(orgId)

  const columns = useMemo<ColumnDef<OrgUser>[]>(
    () => [
      { accessorKey: 'email', header: 'Email' },
      {
        accessorKey: 'full_name',
        header: 'Name',
        cell: ({ row }) => row.original.full_name ?? '—',
      },
      {
        accessorKey: 'role',
        header: 'Role',
        cell: ({ row }) => (
          <Badge variant="outline">
            {row.original.role === 'org_admin' ? 'Org admin' : 'Member'}
          </Badge>
        ),
      },
      {
        accessorKey: 'is_active',
        header: 'Status',
        cell: ({ row }) =>
          row.original.is_active ? (
            <Badge>Active</Badge>
          ) : (
            <Badge variant="outline">Inactive</Badge>
          ),
      },
    ],
    [],
  )

  const rows = users ?? []
  const paged = rows.slice(pageIndex * PAGE_SIZE, (pageIndex + 1) * PAGE_SIZE)

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{orgName} — Users</h2>
        <Button type="button" onClick={() => setAddOpen(true)}>
          <Plus className="mr-2 h-4 w-4" /> Add user
        </Button>
      </div>

      <DataTable<OrgUser>
        columns={columns}
        data={paged}
        total={rows.length}
        pagination={{ pageIndex, pageSize: PAGE_SIZE }}
        onStateChange={(u) => {
          if (typeof u.page === 'number') setPageIndex(u.page - 1)
        }}
        isLoading={isPending}
        error={error as Error | null}
        rowActions={(row) => {
          const isSelf = me?.id === row.id
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button type="button" variant="ghost" size="icon" aria-label={`Actions for ${row.email}`}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{row.email}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  disabled={isSelf}
                  onClick={() =>
                    updateUser.mutate({
                      orgId,
                      userId: row.id,
                      data: { role: row.role === 'org_admin' ? 'member' : 'org_admin' },
                    })
                  }
                >
                  {row.role === 'org_admin' ? 'Demote to member' : 'Promote to org admin'}
                </DropdownMenuItem>
                <DropdownMenuItem
                  disabled={isSelf}
                  onClick={() =>
                    updateUser.mutate({
                      orgId,
                      userId: row.id,
                      data: { is_active: !row.is_active },
                    })
                  }
                >
                  {row.is_active ? 'Deactivate' : 'Reactivate'}
                </DropdownMenuItem>
                <DropdownMenuItem
                  disabled={isSelf}
                  onClick={() =>
                    resetPassword.mutate(
                      { orgId, userId: row.id },
                      {
                        onSuccess: (res) =>
                          setTempPassword({ password: res.temp_password, email: row.email }),
                      },
                    )
                  }
                >
                  Reset password
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        }}
      />

      <UserFormDialog
        orgId={orgId}
        open={addOpen}
        onOpenChange={setAddOpen}
        onCreated={(created) =>
          setTempPassword({ password: created.temp_password, email: created.email })
        }
      />
      <TempPasswordDialog
        password={tempPassword?.password ?? null}
        email={tempPassword?.email ?? null}
        onClose={() => setTempPassword(null)}
      />
    </section>
  )
}
