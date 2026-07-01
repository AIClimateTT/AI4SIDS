import type { LucideIcon } from 'lucide-react'

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
}
