import { AlertTriangle, Bell, Info, MapPin, Clock } from 'lucide-react'
import type { AlertItem, AlertSeverity } from '@/features/shell/types'

const SEVERITY_STYLES: Record<
  AlertSeverity,
  { border: string; bg: string; icon: typeof Bell; iconColor: string }
> = {
  warning: { border: 'border-l-red-500', bg: 'bg-red-50', icon: AlertTriangle, iconColor: 'text-red-500' },
  alert: { border: 'border-l-amber-500', bg: 'bg-amber-50', icon: Bell, iconColor: 'text-amber-500' },
  advisory: { border: 'border-l-blue-500', bg: 'bg-blue-50', icon: Info, iconColor: 'text-blue-500' },
}

export function AlertCard({ alert }: { alert: AlertItem }) {
  const style = SEVERITY_STYLES[alert.severity]
  const Icon = style.icon
  return (
    <div className={`flex gap-3 rounded-lg border border-l-4 ${style.border} ${style.bg} p-3`}>
      <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${style.iconColor}`} />
      <div className="min-w-0 flex-1">
        <div className="font-medium text-slate-900">{alert.title}</div>
        <div className="mt-1 flex items-center gap-1 text-xs text-slate-600">
          <MapPin className="h-3 w-3" />
          {alert.location}
        </div>
        <div className="mt-0.5 flex items-center gap-1 text-xs text-slate-500">
          <Clock className="h-3 w-3" />
          {alert.timestamp}
        </div>
      </div>
    </div>
  )
}

export default AlertCard
