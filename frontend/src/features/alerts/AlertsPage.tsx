import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ALERTS } from '@/features/alerts/data'
import { filterAlerts, type AlertFilter } from '@/features/alerts/filter'
import { AlertCard } from '@/features/alerts/components/AlertCard'

const FILTERS: { key: AlertFilter; label: string; count: number }[] = [
  { key: 'all', label: 'All', count: ALERTS.length },
  { key: 'alert', label: 'Alerts', count: filterAlerts(ALERTS, 'alert').length },
  { key: 'warning', label: 'Warnings', count: filterAlerts(ALERTS, 'warning').length },
]

export function AlertsPage() {
  const [filter, setFilter] = useState<AlertFilter>('all')
  const visible = filterAlerts(ALERTS, filter)

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>Alerts &amp; Notifications</CardTitle>
          <p className="text-sm text-muted-foreground">Active and recent alerts</p>
          <div className="flex gap-2 pt-2">
            {FILTERS.map((f) => (
              <Button
                key={f.key}
                size="sm"
                variant={filter === f.key ? 'default' : 'outline'}
                onClick={() => setFilter(f.key)}
              >
                {f.label} ({f.count})
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {visible.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export default AlertsPage
