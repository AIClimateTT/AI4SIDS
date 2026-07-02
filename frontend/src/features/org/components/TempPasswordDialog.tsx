import { useState } from 'react'
import { Check, Copy } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

/** Shows a generated temporary password exactly once. */
export function TempPasswordDialog({
  password,
  email,
  onClose,
}: {
  password: string | null
  email: string | null
  onClose: () => void
}) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    if (!password) return
    await navigator.clipboard.writeText(password)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <Dialog open={!!password} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Temporary password</DialogTitle>
          <DialogDescription>
            {email ? `For ${email}. ` : ''}This password is shown only once —
            share it securely. The user must change it at first login.
          </DialogDescription>
        </DialogHeader>
        <div className="flex items-center gap-2">
          <code
            data-testid="temp-password"
            className="flex-1 rounded-md bg-muted px-3 py-2 font-mono text-sm"
          >
            {password}
          </code>
          <Button type="button" variant="outline" size="icon" onClick={copy} aria-label="Copy password">
            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          </Button>
        </div>
        <DialogFooter>
          <Button type="button" onClick={onClose}>
            Done
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
