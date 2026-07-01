import type { AlertItem } from '@/features/shell/types'

export const ALERTS: AlertItem[] = [
  {
    id: 'a1',
    title: 'Heavy Rainfall Warning',
    location: 'Eastern Trinidad',
    timestamp: 'May 21, 2025 8:30 AM',
    severity: 'warning',
  },
  {
    id: 'a2',
    title: 'Flood Watch',
    location: 'Caroni Basin',
    timestamp: 'May 21, 2025 7:45 AM',
    severity: 'alert',
  },
  {
    id: 'a3',
    title: 'Small Craft Advisory',
    location: 'Coastal Waters',
    timestamp: 'May 21, 2025 7:48 AM',
    severity: 'advisory',
  },
  {
    id: 'a4',
    title: 'High Tide Advisory',
    location: 'Port of Spain',
    timestamp: 'May 21, 2025 6:30 AM',
    severity: 'alert',
  },
  {
    id: 'a5',
    title: 'Landslide Warning',
    location: 'Northern Range',
    timestamp: 'May 21, 2025 6:10 AM',
    severity: 'warning',
  },
  {
    id: 'a6',
    title: 'River Level Alert',
    location: 'Sangre Grande',
    timestamp: 'May 21, 2025 5:55 AM',
    severity: 'alert',
  },
]
