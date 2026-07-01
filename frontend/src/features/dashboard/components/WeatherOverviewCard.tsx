import { Cloud, Droplets, Wind } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { WEATHER, UPCOMING_EVENTS } from '@/features/dashboard/data'

export function WeatherOverviewCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Weather Overview</CardTitle>
        <p className="text-xs text-muted-foreground">{WEATHER.place}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-4xl font-bold">{WEATHER.temperatureC}°C</div>
            <div className="text-sm text-muted-foreground">{WEATHER.condition}</div>
          </div>
          <Cloud className="h-12 w-12 text-amber-400" />
        </div>
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div className="flex items-center gap-1">
            <Droplets className="h-4 w-4 text-blue-500" />
            {WEATHER.rainfallMm} mm
          </div>
          <div className="flex items-center gap-1">
            <Wind className="h-4 w-4 text-slate-500" />
            {WEATHER.windKmh} km/h
          </div>
          <div className="flex items-center gap-1">
            <Droplets className="h-4 w-4 text-cyan-500" />
            {WEATHER.humidityPct}%
          </div>
        </div>
        <div>
          <div className="mb-2 text-sm font-semibold">Upcoming Events</div>
          <div className="space-y-2">
            {UPCOMING_EVENTS.map((e) => (
              <div key={e.id} className="flex items-center justify-between rounded-md border p-2">
                <div>
                  <div className="text-sm font-medium">{e.title}</div>
                  <div className="text-xs text-muted-foreground">{e.date}</div>
                </div>
                <Badge variant="outline">{e.tag}</Badge>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default WeatherOverviewCard
