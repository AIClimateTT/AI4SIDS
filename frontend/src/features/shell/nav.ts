import {
  LayoutDashboard,
  Radio,
  ShieldAlert,
  Bell,
  Bot,
  BookOpen,
  BarChart3,
  Database,
  Settings,
} from 'lucide-react'
import type { NavItem } from '@/features/shell/types'

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Real-time Monitoring', to: '/dashboard/monitoring', icon: Radio },
  { label: 'Risk & Vulnerability', to: '/dashboard/risk', icon: ShieldAlert },
  { label: 'Alerts & Notifications', to: '/dashboard/alerts', icon: Bell, badge: 6 },
  { label: 'AI Preparedness Assistant', to: '/dashboard/assistant', icon: Bot },
  { label: 'Resources & Guidance', to: '/dashboard/resources', icon: BookOpen },
  { label: 'Reports & Analytics', to: '/dashboard/reports', icon: BarChart3 },
  { label: 'Data Management', to: '/dashboard/data', icon: Database },
  { label: 'Settings', to: '/dashboard/settings', icon: Settings },
]

export function getNavItemByPath(pathname: string): NavItem | undefined {
  // Strip trailing slash (except root) for stable exact matching.
  const path = pathname.length > 1 ? pathname.replace(/\/$/, '') : pathname
  return NAV_ITEMS.find((item) => item.to === path)
}
