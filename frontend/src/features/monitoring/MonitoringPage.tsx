import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BaseMap } from '@/features/shell/components/BaseMap'
import {
  RAINFALL_STATIONS,
  RAINFALL_MARKERS,
  rainfallColor,
} from '@/features/monitoring/data'

const EMPTY_TABS = ['River Levels', 'Weather Stations', 'Tide Levels']

export function MonitoringPage() {
  return (
    <div className="space-y-4 p-6">
      <div>
        <h2 className="text-xl font-bold">Real-time Monitoring</h2>
        <p className="text-sm text-muted-foreground">Live feeds and sensor data</p>
      </div>

      <Tabs defaultValue="rainfall">
        <TabsList>
          <TabsTrigger value="rainfall">Rainfall</TabsTrigger>
          <TabsTrigger value="river">River Levels</TabsTrigger>
          <TabsTrigger value="stations">Weather Stations</TabsTrigger>
          <TabsTrigger value="tide">Tide Levels</TabsTrigger>
        </TabsList>

        <TabsContent value="rainfall">
          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardContent className="pt-6">
                <BaseMap markers={RAINFALL_MARKERS} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Rainfall (mm) — Last 24h</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {RAINFALL_STATIONS.map((s) => (
                  <div key={s.id} className="flex items-center justify-between text-sm">
                    <span>{s.name}</span>
                    <span className="font-semibold" style={{ color: rainfallColor(s.mm) }}>
                      {s.mm} mm
                    </span>
                  </div>
                ))}
                <button type="button" className="pt-2 text-sm font-medium text-blue-600 hover:underline">
                  View all stations →
                </button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {EMPTY_TABS.map((label, i) => (
          <TabsContent key={label} value={['river', 'stations', 'tide'][i]}>
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                No additional data in this demo.
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      <p className="text-xs text-muted-foreground">
        Data updates every 15 minutes · Next update 10:45 AM
      </p>
    </div>
  )
}

export default MonitoringPage
