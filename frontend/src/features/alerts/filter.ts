import type { AlertItem } from '@/features/shell/types'

export type AlertFilter = 'all' | 'alert' | 'warning'

export function filterAlerts(
  alerts: AlertItem[],
  filter: AlertFilter,
): AlertItem[] {
  if (filter === 'all') return alerts
  return alerts.filter((a) => a.severity === filter)
}
