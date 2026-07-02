import { Link } from '@tanstack/react-router'
import { Waves } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { NAV_ITEMS, filterNavByRole } from '@/features/shell/nav'
import { ThemeToggle } from '@/features/shell/components/ThemeToggle'
import { useAuth } from '@/lib/auth/AuthContext'

export function GovSidebar() {
  const { user } = useAuth()
  const items = filterNavByRole(NAV_ITEMS, user?.role ?? null)
  return (
    <aside className="flex h-full w-64 flex-col bg-slate-900 text-slate-100">
      {/* Brand */}
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
          <Waves className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="text-base font-bold leading-tight">AI4SIDS-Gov</div>
          <div className="text-[11px] leading-tight text-slate-400">
            Climate Resilience &amp; Preparedness Platform
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-2">
        {items.map(({ label, to, icon: Icon, badge }) => (
          <Link
            key={to}
            to={to}
            activeOptions={{ exact: to === '/dashboard' }}
            activeProps={{ className: 'bg-blue-600 text-white hover:bg-blue-600' }}
            inactiveProps={{ className: 'text-slate-300 hover:bg-white/10 hover:text-white' }}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span className="flex-1">{label}</span>
            {badge ? (
              <Badge className="bg-red-500 px-1.5 text-[11px] text-white hover:bg-red-500">
                {badge}
              </Badge>
            ) : null}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/10 px-3 py-3">
        <ThemeToggle />
        <div className="px-3 pt-2 text-[11px] text-slate-500">v1.0.0</div>
      </div>
    </aside>
  )
}

export default GovSidebar
