import type { LucideIcon } from 'lucide-react'
import type { Role } from '@/lib/auth/types'

export type AlertSeverity = 'warning' | 'alert' | 'advisory'

export interface AlertItem {
  id: string
  title: string
  location: string
  timestamp: string
  severity: AlertSeverity
}

export interface NavItem {
  label: string
  to: string
  icon: LucideIcon
  badge?: number
  /** If set, only these roles (plus super_admin) see the item. */
  roles?: Role[]
}
