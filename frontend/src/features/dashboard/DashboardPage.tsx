import { Download, Settings2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BaseMap } from '@/features/shell/components/BaseMap'
import { StatCard } from '@/features/dashboard/components/StatCard'
import { WeatherOverviewCard } from '@/features/dashboard/components/WeatherOverviewCard'
import { STATS, RISK_MARKERS } from '@/features/dashboard/data'
import { AlertCard } from '@/features/alerts/components/AlertCard'
import { ALERTS } from '@/features/alerts/data'

export function DashboardPage() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">National Overview</h2>
          <p className="text-sm text-muted-foreground">Trinidad &amp; Tobago</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
          <Button variant="outline" size="sm">
            <Settings2 className="mr-2 h-4 w-4" />
            Customise
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        {STATS.map((s) => (
          <StatCard key={s.id} stat={s} />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Risk Map</CardTitle>
          </CardHeader>
          <CardContent>
            <BaseMap markers={RISK_MARKERS} />
          </CardContent>
        </Card>
        <WeatherOverviewCard />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Alerts &amp; Notifications</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          {ALERTS.slice(0, 3).map((a) => (
            <AlertCard key={a.id} alert={a} />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export default DashboardPage
