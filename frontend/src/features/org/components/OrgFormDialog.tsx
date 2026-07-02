import { useEffect, useState, type FormEvent } from 'react'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCreateOrg, useUpdateOrg } from '@/lib/queries/orgs'
import type { Org } from '@/lib/api/orgs.types'

/** Create (org == null) or edit (org != null) an organization. */
export function OrgFormDialog({
  org,
  open,
  onOpenChange,
}: {
  org: Org | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const createOrg = useCreateOrg(() => onOpenChange(false))
  const updateOrg = useUpdateOrg(() => onOpenChange(false))
  const isPending = createOrg.isPending || updateOrg.isPending

  useEffect(() => {
    if (open) {
      setName(org?.name ?? '')
      setDescription(org?.description ?? '')
    }
  }, [open, org])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (org) {
      updateOrg.mutate({ id: org.id, data: { name, description } })
    } else {
      createOrg.mutate({ name, description: description || undefined })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{org ? 'Edit organization' : 'New organization'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <Label htmlFor="org-name">Name</Label>
            <Input
              id="org-name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="org-description">Description</Label>
            <Input
              id="org-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Saving…' : org ? 'Save changes' : 'Create organization'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
