export interface SystemService {
  id: string
  label: string
  status: 'Operational'
  detail: string
}

export const SYSTEM_STATUS: SystemService[] = [
  { id: 'daily', label: 'Daily Services', status: 'Operational', detail: 'Last run 8:00 AM' },
  { id: 'sensors', label: 'Last 5 Sensors', status: 'Operational', detail: 'All reporting' },
  { id: 'alerts', label: 'Alerts System', status: 'Operational', detail: 'Live' },
  { id: 'backup', label: 'Last Backup', status: 'Operational', detail: '2:00 AM' },
]

export interface ReportType {
  id: string
  label: string
  description: string
}

export const REPORT_TYPES: ReportType[] = [
  { id: 'daily', label: 'Daily Situation Report', description: 'Snapshot of the last 24 hours.' },
  { id: 'weekly', label: 'Weekly Report', description: 'Trends across the past 7 days.' },
  { id: 'custom', label: 'Custom Report', description: 'Choose range and metrics.' },
]
