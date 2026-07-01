import {
  Home,
  Route as RouteIcon,
  Phone,
  Megaphone,
  FileText,
  CalendarDays,
  FileCog,
  type LucideIcon,
} from 'lucide-react'

export interface ResourceLink {
  id: string
  label: string
  hint: string
  icon: LucideIcon
}

export const PREPAREDNESS_RESOURCES: ResourceLink[] = [
  { id: 'shelter', label: 'Shelter Directory', hint: 'View locations', icon: Home },
  { id: 'routes', label: 'Evacuation Routes', hint: 'View map', icon: RouteIcon },
  { id: 'contacts', label: 'Emergency Contacts', hint: 'View directory', icon: Phone },
  { id: 'awareness', label: 'Public Awareness', hint: 'View materials', icon: Megaphone },
]

export const QUICK_REPORTS: ResourceLink[] = [
  { id: 'daily', label: 'Daily Situation Report', hint: 'Generate', icon: FileText },
  { id: 'weekly', label: 'Weekly Report', hint: 'Generate', icon: CalendarDays },
  { id: 'custom', label: 'Custom Report', hint: 'Configure', icon: FileCog },
]

export const DATA_PARTNERS: string[] = [
  'TTMS',
  'ODPM',
  'MPAAI',
  'Ministry of Health',
  'CSO',
  'Regional Corporations',
]
