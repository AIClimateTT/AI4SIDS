import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import {
  MapPin,
  Info,
  Droplets,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react'
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  Polygon,
} from 'react-leaflet'
import { useLocations, useRealTimeConditions } from '@/lib/hooks/useApiData'
import { mapApiRiskToComponent, getRiskColor } from '@/lib/utils/riskMapping'
import { useState } from 'react'
import type { RealTimeConditions } from '@/lib/api/types'
import 'leaflet/dist/leaflet.css'

// Location Details Component
interface LocationDetailsProps {
  realTimeData?: RealTimeConditions
}

function LocationDetails({ realTimeData }: LocationDetailsProps) {
  if (!realTimeData) {
    return (
      <div className="py-4 px-2">
        <div className="flex items-center justify-center text-sm text-muted-foreground">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary mr-2"></div>
          Loading real-time data...
        </div>
      </div>
    )
  }

  const getTrendIcon = (trend: string) => {
    switch (trend?.toLowerCase()) {
      case 'rising':
        return <TrendingUp className="h-4 w-4 text-red-500" />
      case 'falling':
        return <TrendingDown className="h-4 w-4 text-green-500" />
      case 'stable':
        return <Minus className="h-4 w-4 text-gray-500" />
      default:
        return null
    }
  }

  return (
    <div className="space-y-4 py-2 px-2">
      {/* Basic Info */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Coordinates</p>
          <p className="font-medium">
            {realTimeData.river_conditions.sensor_id}
          </p>
        </div>
        <div>
          <p className="text-muted-foreground">Last Updated</p>
          <p className="font-medium text-xs">
            {new Date(realTimeData.timestamp).toLocaleTimeString()}
          </p>
        </div>
      </div>

      {/* River Conditions */}
      <div className="border-t pt-3">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-semibold flex items-center gap-2">
            <Droplets className="h-4 w-4 text-blue-500" />
            River Conditions
          </h4>
          <Badge
            className={getRiskColor(
              mapApiRiskToComponent(realTimeData.river_conditions.flood_risk),
            )}
          >
            {realTimeData.river_conditions.flood_risk}
          </Badge>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-muted-foreground">Water Level</p>
            <p className="text-lg font-bold text-blue-600">
              {realTimeData.river_conditions.level.toFixed(2)}m
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Trend</p>
            <p className="font-medium flex items-center gap-1">
              {getTrendIcon(realTimeData.river_conditions.trend)}
              <span className="capitalize">
                {realTimeData.river_conditions.trend}
              </span>
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Change Rate</p>
            <p className="font-medium">
              {realTimeData.river_conditions.change_rate > 0 ? '+' : ''}
              {realTimeData.river_conditions.change_rate.toFixed(3)}m
            </p>
          </div>
        </div>
      </div>

      {/* Weather Conditions */}
      <div className="border-t pt-3">
        <h4 className="text-sm font-semibold mb-2">Weather Conditions</h4>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-muted-foreground">Rainfall (15min)</p>
            <p className="font-bold text-blue-600">
              {realTimeData.weather.rainfall_mm.toFixed(1)}mm
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Temperature</p>
            <p className="font-medium">
              {realTimeData.weather.temperature_c.toFixed(1)}°C
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Humidity</p>
            <p className="font-medium">
              {realTimeData.weather.humidity_percent}%
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Rain Rate</p>
            <p className="font-medium">
              {realTimeData.weather.rainfall_rate_hourly.toFixed(1)}mm/hr
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

const RiskMap = () => {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)

  // Fetch comprehensive system update (includes more data than just locations)
  const { data: systemData, isLoading, error } = useLocations()

  // Fetch real-time data for selected location
  const { data: realTimeData } = useRealTimeConditions(
    selectedLocation,
    !!selectedLocation,
  )

  // Transform API locations to map format
  const riskLevels =
    systemData?.locations?.map((location) => ({
      zone: location.name,
      risk: mapApiRiskToComponent(location.current_risk),
      lat: location.latitude,
      lng: location.longitude,
      sensorId: location.sensor_id,
    })) || []

  const getRiskColor = (risk: string) => {
    const colors = {
      critical: 'bg-critical text-critical-foreground',
      'high-risk': 'bg-high-risk text-high-risk-foreground',
      moderate: 'bg-moderate text-moderate-foreground',
      'low-risk': 'bg-low-risk text-low-risk-foreground',
      safe: 'bg-safe text-safe-foreground',
    }
    return colors[risk as keyof typeof colors] || ''
  }

  const getRiskHexColor = (risk: string) => {
    const colors = {
      critical: '#ef4444',
      'high-risk': '#f97316',
      moderate: '#eab308',
      'low-risk': '#84cc16',
      safe: '#22c55e',
    }
    return colors[risk as keyof typeof colors] || '#6b7280'
  }

  // Helper component to ensure Leaflet coordinates are in [lat, lng] format
  const convertToLatLng = (coords: [number, number][]): [number, number][] => {
    // Leaflet uses [lat, lng], our data is [lng, lat], so we need to swap
    return coords.map((coord) => [coord[1], coord[0]] as [number, number])
  }

  return (
    <section className="py-16 px-6">
      <div className="container mx-auto">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Map Visualization */}
          <div className="col-span-1">
            <Card
              className="shadow-lg flex flex-col"
              
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-primary" />
                  Interactive Flood Risk Map
                </CardTitle>
                <CardDescription>
                  Color-coded flood risk zones across Caribbean SIDS
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="h-[400px] w-full rounded-lg overflow-hidden border-2 border-border relative">
                  <MapContainer
                    center={[10.5, -61.3]} // Trinidad center
                    zoom={9}
                    zoomControl={true}
                    style={{ width: '100%', height: '100%', zIndex: 1 }}
                  >
                    <TileLayer
                      url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                      maxZoom={19}
                      attribution='© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    />

                    {/* Render city markers */}
                    {riskLevels.map((zone) => (
                      <CircleMarker
                        key={zone.zone}
                        center={[zone.lat, zone.lng]}
                        radius={10}
                        pathOptions={{
                          color: getRiskHexColor(zone.risk),
                          fillColor: getRiskHexColor(zone.risk),
                          fillOpacity: 0.7,
                          weight: 2,
                        }}
                      >
                        <Popup>
                          <div className="min-w-[200px]">
                            <div className="font-bold text-base mb-2">
                              {zone.zone}
                            </div>
                            <div className="space-y-1 text-xs">
                              <div className="flex justify-between">
                                <span>Risk:</span>
                                <span
                                  style={{
                                    color: getRiskHexColor(zone.risk),
                                    fontWeight: 'bold',
                                  }}
                                >
                                  {zone.risk.replace('-', ' ').toUpperCase()}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span>Sensor ID:</span>
                                <span className="text-gray-600">
                                  {zone.sensorId}
                                </span>
                              </div>
                            </div>
                          </div>
                        </Popup>
                      </CircleMarker>
                    ))}
                  </MapContainer>

                  {/* Legend */}
                  <div className="absolute bottom-4 left-4 bg-background/95 backdrop-blur-sm p-3 rounded-lg border shadow-lg">
                    <div className="text-xs font-semibold mb-2">
                      Flood Risk Levels
                    </div>
                    <div className="space-y-1 text-xs">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-critical"></div>
                        <span>Critical</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-high-risk"></div>
                        <span>High</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-moderate"></div>
                        <span>Moderate</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-low-risk"></div>
                        <span>Low</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-safe"></div>
                        <span>Safe</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Legend */}
                <div className="space-y-3">
                  <div className="text-sm font-semibold">Flood Risk Levels</div>
                  <div className="grid grid-cols-5 gap-3">
                    <div className="text-center">
                      <div className="w-full h-8 rounded-md bg-critical mb-2"></div>
                      <div className="text-xs font-medium">Critical</div>
                      <div className="text-xs text-muted-foreground">≥4.2m</div>
                    </div>
                    <div className="text-center">
                      <div className="w-full h-8 rounded-md bg-high-risk mb-2"></div>
                      <div className="text-xs font-medium">High</div>
                      <div className="text-xs text-muted-foreground">
                        3.6-4.2m
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="w-full h-8 rounded-md bg-moderate mb-2"></div>
                      <div className="text-xs font-medium">Moderate</div>
                      <div className="text-xs text-muted-foreground">
                        3.0-3.6m
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="w-full h-8 rounded-md bg-low-risk mb-2"></div>
                      <div className="text-xs font-medium">Low</div>
                      <div className="text-xs text-muted-foreground">
                        2.7-3.0m
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="w-full h-8 rounded-md bg-safe mb-2"></div>
                      <div className="text-xs font-medium">Safe</div>
                      <div className="text-xs text-muted-foreground">
                        &lt;2.7m
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground text-center pt-2 border-t">
                    River levels measured in meters above baseline
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          {/* Risk Zone Details */}
          <div className="space-y-6">
            <Card
              className="shadow-lg flex flex-col"
              style={{ height: '650px' }}
            >
              <CardHeader>
                <CardTitle>Current Risk Zones</CardTitle>
                <CardDescription>
                  <Info className="inline-block mr-1" size={'24'} />
                  <span className="text-foreground">
                    Click on a zone for real-time details
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent className="overflow-y-auto flex-1">
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Loading locations...
                    </p>
                  </div>
                ) : error ? (
                  <div className="text-center py-8 text-red-600">
                    <p>Failed to load locations</p>
                  </div>
                ) : (
                  <Accordion type="single" collapsible className="w-full">
                    {riskLevels.map((zone) => (
                      <AccordionItem key={zone.zone} value={zone.zone}>
                        <AccordionTrigger
                          className="hover:no-underline"
                          onClick={() =>
                            setSelectedLocation(
                              selectedLocation === zone.zone ? null : zone.zone,
                            )
                          }
                        >
                          <div className="flex items-center justify-between w-full pr-4">
                            <div className="flex items-center gap-3">
                              <MapPin className="h-5 w-5 text-muted-foreground" />
                              <div className="text-left">
                                <div className="font-semibold">{zone.zone}</div>
                                <div className="text-sm text-muted-foreground">
                                  Sensor: {zone.sensorId}
                                </div>
                              </div>
                            </div>
                            <Badge className={getRiskColor(zone.risk)}>
                              {zone.risk.replace('-', ' ').toUpperCase()}
                            </Badge>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent>
                          <LocationDetails
                            realTimeData={
                              selectedLocation === zone.zone
                                ? realTimeData
                                : undefined
                            }
                          />
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  )
}

export default RiskMap
