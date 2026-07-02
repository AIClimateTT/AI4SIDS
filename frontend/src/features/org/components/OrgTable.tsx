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
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { orgQueries, useUpdateOrg } from '@/lib/queries/orgs'
import type { Org } from '@/lib/api/orgs.types'
import { OrgFormDialog } from './OrgFormDialog'

const PAGE_SIZE = 10

export function OrgTable({ onManageUsers }: { onManageUsers: (org: Org) => void }) {
  const { data: orgs, isPending, error } = useQuery(orgQueries.list())
  const [pageIndex, setPageIndex] = useState(0)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Org | null>(null)
  const updateOrg = useUpdateOrg()

  const columns = useMemo<ColumnDef<Org>[]>(
    () => [
      { accessorKey: 'name', header: 'Organization' },
      {
        accessorKey: 'description',
        header: 'Description',
        cell: ({ row }) => row.original.description ?? '—',
      },
      { accessorKey: 'user_count', header: 'Users' },
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

  const rows = orgs ?? []
  const paged = rows.slice(pageIndex * PAGE_SIZE, (pageIndex + 1) * PAGE_SIZE)

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Organizations</h2>
        <Button
          type="button"
          onClick={() => {
            setEditing(null)
            setFormOpen(true)
          }}
        >
          <Plus className="mr-2 h-4 w-4" /> New organization
        </Button>
      </div>

      <DataTable<Org>
        columns={columns}
        data={paged}
        total={rows.length}
        pagination={{ pageIndex, pageSize: PAGE_SIZE }}
        onStateChange={(u) => {
          if (typeof u.page === 'number') setPageIndex(u.page - 1)
        }}
        isLoading={isPending}
        error={error as Error | null}
        rowActions={(org) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button type="button" variant="ghost" size="icon" aria-label={`Actions for ${org.name}`}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onManageUsers(org)}>
                Manage users
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  setEditing(org)
                  setFormOpen(true)
                }}
              >
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() =>
                  updateOrg.mutate({ id: org.id, data: { is_active: !org.is_active } })
                }
              >
                {org.is_active ? 'Deactivate' : 'Reactivate'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      />

      <OrgFormDialog org={editing} open={formOpen} onOpenChange={setFormOpen} />
    </section>
  )
}
