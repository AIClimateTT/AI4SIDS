import { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
  ComposedChart,
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Download,
  Maximize2,
  MapPin,
  Clock,
} from 'lucide-react'

// Mock data for the past 7 days
const rainfallData = [
  { date: 'Mon', value: 12 },
  { date: 'Tue', value: 25 },
  { date: 'Wed', value: 45 },
  { date: 'Thu', value: 38 },
  { date: 'Fri', value: 52 },
  { date: 'Sat', value: 28 },
  { date: 'Sun', value: 15 },
]

const riverGaugeData = [
  { date: 'Mon', level: 2.3 },
  { date: 'Tue', level: 2.8 },
  { date: 'Wed', level: 3.5 },
  { date: 'Thu', level: 3.2 },
  { date: 'Fri', level: 4.1 },
  { date: 'Sat', level: 3.6 },
  { date: 'Sun', level: 2.9 },
]

const temperatureData = [
  { date: 'Mon', temp: 28 },
  { date: 'Tue', temp: 29 },
  { date: 'Wed', temp: 27 },
  { date: 'Thu', temp: 30 },
  { date: 'Fri', temp: 31 },
  { date: 'Sat', temp: 29 },
  { date: 'Sun', temp: 28 },
]

const humidityData = [
  { date: 'Mon', humidity: 65 },
  { date: 'Tue', humidity: 72 },
  { date: 'Wed', humidity: 78 },
  { date: 'Thu', humidity: 68 },
  { date: 'Fri', humidity: 82 },
  { date: 'Sat', humidity: 75 },
  { date: 'Sun', humidity: 70 },
]

const DataAnalytics = () => {
  const [timeRange, setTimeRange] = useState('realtime')
  const [location, setLocation] = useState('caroni')

  // Determine if we're in real-time mode
  const isRealTime = timeRange === 'realtime'

  // Calculate statistics
  const rainfallStats = {
    current: 15,
    avg: 30.7,
    max: 52,
    min: 12,
    trend: -28.8,
  }

  const riverStats = {
    current: 2.9,
    avg: 3.2,
    max: 4.1,
    min: 2.3,
    trend: 8.2,
  }

  const tempStats = {
    current: 28,
    avg: 29,
    max: 31,
    min: 27,
    trend: -3.4,
  }

  const humidityStats = {
    current: 70,
    avg: 72.9,
    max: 82,
    min: 65,
    trend: 2.1,
  }

  // Combined data for rainfall and river levels
  const combinedData = [
    { date: 'Mon', rainfall: 12, riverLevel: 2.3 },
    { date: 'Tue', rainfall: 25, riverLevel: 2.8 },
    { date: 'Wed', rainfall: 45, riverLevel: 3.5 },
    { date: 'Thu', rainfall: 38, riverLevel: 3.2 },
    { date: 'Fri', rainfall: 52, riverLevel: 4.1 },
    { date: 'Sat', rainfall: 28, riverLevel: 3.6 },
    { date: 'Sun', rainfall: 15, riverLevel: 2.9 },
  ]

  return (
    <div className="container py-12 px-6 mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold mb-3">Data Analytics</h2>
        <p className="text-muted-foreground text-lg">
          Real-time environmental monitoring data for informed decision-making
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-col md:flex-row gap-4 mb-8 justify-between items-center">
        <div className="flex flex-wrap gap-3">
          <Select value={location} onValueChange={setLocation}>
            <SelectTrigger className="w-[180px]">
              <MapPin className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="caroni">Caroni</SelectItem>
              <SelectItem value="arima">St.Augustine</SelectItem>
              <SelectItem value="diego">Chaguanas</SelectItem>
              <SelectItem value="point">Cunupia</SelectItem>
              <SelectItem value="sthelena">St. Helena</SelectItem>
              <SelectItem value="piarco">Piarco</SelectItem>
              <SelectItem value="laslomas">Las Lomas</SelectItem>
              <SelectItem value="kellyvillage">Kelly Village</SelectItem>
            </SelectContent>
          </Select>

          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[140px]">
              <Clock className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="realtime">Real-time</SelectItem>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="custom">Custom Range</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex gap-2">
          {isRealTime ? (
            <Badge variant="outline" className="animate-pulse-subtle">
              <div className="h-2 w-2 rounded-full bg-safe mr-2" />
              Live • Updated 2 min ago
            </Badge>
          ) : (
            <Badge variant="outline">
              <Clock className="h-3 w-3 mr-2" />
              Historical Data •{' '}
              {timeRange === '24h'
                ? 'Last 24 Hours'
                : timeRange === '7d'
                  ? 'Last 7 Days'
                  : timeRange === '30d'
                    ? 'Last 30 Days'
                    : 'Custom Range'}
            </Badge>
          )}
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rainfall Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle>Rainfall</CardTitle>
                <CardDescription>
                  7-day rainfall measurements (mm)
                </CardDescription>
              </div>
              <Button variant="ghost" size="sm">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex gap-4 mt-4">
              <div>
                <div className="text-2xl font-bold">
                  {rainfallStats.current}mm
                </div>
                <div className="text-xs text-muted-foreground">Current</div>
              </div>
              <div>
                <div className="text-sm font-semibold">
                  {rainfallStats.avg}mm
                </div>
                <div className="text-xs text-muted-foreground">Average</div>
              </div>
              <div>
                <div className="text-sm font-semibold">
                  {rainfallStats.max}mm
                </div>
                <div className="text-xs text-muted-foreground">Peak</div>
              </div>
              <div className="flex items-center gap-1">
                {rainfallStats.trend < 0 ? (
                  <>
                    <TrendingDown className="h-4 w-4 text-safe" />
                    <span className="text-sm font-semibold text-safe">
                      {Math.abs(rainfallStats.trend)}%
                    </span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-4 w-4 text-high-risk" />
                    <span className="text-sm font-semibold text-high-risk">
                      +{rainfallStats.trend}%
                    </span>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={rainfallData}>
                <defs>
                  <linearGradient
                    id="rainfallGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="var(--primary)"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="var(--primary)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  className="stroke-border"
                  opacity={0.3}
                />
                <XAxis
                  dataKey="date"
                  className="text-xs"
                  stroke="var(--muted-foreground)"
                />
                <YAxis className="text-xs" stroke="var(--muted-foreground)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                />
                <ReferenceLine
                  y={40}
                  stroke="var(--color-high-risk)"
                  strokeDasharray="3 3"
                  label="Warning"
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="var(--primary)"
                  strokeWidth={2}
                  fill="url(#rainfallGradient)"
                  name="Rainfall (mm)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* River Gauge Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle>River Gauge</CardTitle>
                <CardDescription>
                  7-day water level measurements (meters)
                </CardDescription>
              </div>
              <Button variant="ghost" size="sm">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex gap-4 mt-4">
              <div>
                <div className="text-2xl font-bold">{riverStats.current}m</div>
                <div className="text-xs text-muted-foreground">Current</div>
              </div>
              <div>
                <div className="text-sm font-semibold">{riverStats.avg}m</div>
                <div className="text-xs text-muted-foreground">Average</div>
              </div>
              <div>
                <div className="text-sm font-semibold">{riverStats.max}m</div>
                <div className="text-xs text-muted-foreground">Peak</div>
              </div>
              <div className="flex items-center gap-1">
                {riverStats.trend < 0 ? (
                  <>
                    <TrendingDown className="h-4 w-4 text-safe" />
                    <span className="text-sm font-semibold text-safe">
                      {Math.abs(riverStats.trend)}%
                    </span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-4 w-4 text-high-risk" />
                    <span className="text-sm font-semibold text-high-risk">
                      +{riverStats.trend}%
                    </span>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={riverGaugeData}>
                <defs>
                  <linearGradient
                    id="riverGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="var(--color-low-risk)"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="var(--color-low-risk)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  className="stroke-border"
                  opacity={0.3}
                />
                <XAxis
                  dataKey="date"
                  className="text-xs"
                  stroke="var(--muted-foreground)"
                />
                <YAxis
                  className="text-xs"
                  stroke="var(--muted-foreground)"
                  domain={[0, 5]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                />
                <ReferenceLine
                  y={3.5}
                  stroke="var(--color-moderate)"
                  strokeDasharray="3 3"
                  label="Alert"
                />
                <ReferenceLine
                  y={4.5}
                  stroke="var(--color-critical)"
                  strokeDasharray="3 3"
                  label="Critical"
                />
                <Area
                  type="monotone"
                  dataKey="level"
                  stroke="var(--color-low-risk)"
                  strokeWidth={2}
                  fill="url(#riverGradient)"
                  name="Water Level (m)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Temperature Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle>Temperature</CardTitle>
                <CardDescription>
                  7-day temperature readings (°C)
                </CardDescription>
              </div>
              <Button variant="ghost" size="sm">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex gap-4 mt-4">
              <div>
                <div className="text-2xl font-bold">{tempStats.current}°C</div>
                <div className="text-xs text-muted-foreground">Current</div>
              </div>
              <div>
                <div className="text-sm font-semibold">{tempStats.avg}°C</div>
                <div className="text-xs text-muted-foreground">Average</div>
              </div>
              <div>
                <div className="text-sm font-semibold">{tempStats.max}°C</div>
                <div className="text-xs text-muted-foreground">Peak</div>
              </div>
              <div className="flex items-center gap-1">
                {tempStats.trend < 0 ? (
                  <>
                    <TrendingDown className="h-4 w-4 text-safe" />
                    <span className="text-sm font-semibold text-safe">
                      {Math.abs(tempStats.trend)}%
                    </span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-4 w-4 text-high-risk" />
                    <span className="text-sm font-semibold text-high-risk">
                      +{tempStats.trend}%
                    </span>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={temperatureData}>
                <defs>
                  <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor="var(--color-high-risk)"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="var(--color-high-risk)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  className="stroke-border"
                  opacity={0.3}
                />
                <XAxis
                  dataKey="date"
                  className="text-xs"
                  stroke="var(--muted-foreground)"
                />
                <YAxis
                  className="text-xs"
                  stroke="var(--muted-foreground)"
                  domain={[20, 35]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="temp"
                  stroke="var(--color-high-risk)"
                  strokeWidth={2}
                  fill="url(#tempGradient)"
                  name="Temperature (°C)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Humidity Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle>Humidity</CardTitle>
                <CardDescription>7-day humidity levels (%)</CardDescription>
              </div>
              <Button variant="ghost" size="sm">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex gap-4 mt-4">
              <div>
                <div className="text-2xl font-bold">
                  {humidityStats.current}%
                </div>
                <div className="text-xs text-muted-foreground">Current</div>
              </div>
              <div>
                <div className="text-sm font-semibold">
                  {humidityStats.avg}%
                </div>
                <div className="text-xs text-muted-foreground">Average</div>
              </div>
              <div>
                <div className="text-sm font-semibold">
                  {humidityStats.max}%
                </div>
                <div className="text-xs text-muted-foreground">Peak</div>
              </div>
              <div className="flex items-center gap-1">
                {humidityStats.trend < 0 ? (
                  <>
                    <TrendingDown className="h-4 w-4 text-safe" />
                    <span className="text-sm font-semibold text-safe">
                      {Math.abs(humidityStats.trend)}%
                    </span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-4 w-4 text-high-risk" />
                    <span className="text-sm font-semibold text-high-risk">
                      +{humidityStats.trend}%
                    </span>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={humidityData}>
                <defs>
                  <linearGradient
                    id="humidityGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="var(--accent)"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="var(--accent)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  className="stroke-border"
                  opacity={0.3}
                />
                <XAxis
                  dataKey="date"
                  className="text-xs"
                  stroke="var(--muted-foreground)"
                />
                <YAxis
                  className="text-xs"
                  stroke="var(--muted-foreground)"
                  domain={[0, 100]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="humidity"
                  stroke="var(--accent)"
                  strokeWidth={2}
                  fill="url(#humidityGradient)"
                  name="Humidity (%)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Combined Rainfall & River Level Chart */}
      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>Rainfall & River Level Correlation</CardTitle>
              <CardDescription>
                Combined view showing the relationship between rainfall and
                water levels
              </CardDescription>
            </div>
            <Button variant="ghost" size="sm">
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <ComposedChart data={combinedData}>
              <defs>
                <linearGradient
                  id="combinedRainfallGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="5%"
                    stopColor="var(--primary)"
                    stopOpacity={0.2}
                  />
                  <stop
                    offset="95%"
                    stopColor="var(--primary)"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                className="stroke-border"
                opacity={0.3}
              />
              <XAxis
                dataKey="date"
                className="text-xs"
                stroke="var(--muted-foreground)"
              />
              <YAxis
                yAxisId="left"
                className="text-xs"
                stroke="var(--primary)"
                label={{
                  value: 'Rainfall (mm)',
                  angle: -90,
                  position: 'insideLeft',
                }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                className="text-xs"
                stroke="var(--color-low-risk)"
                label={{
                  value: 'Water Level (m)',
                  angle: 90,
                  position: 'insideRight',
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--card)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                }}
              />
              <Legend />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="rainfall"
                stroke="var(--primary)"
                strokeWidth={2}
                fill="url(#combinedRainfallGradient)"
                name="Rainfall (mm)"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="riverLevel"
                stroke="var(--color-low-risk)"
                strokeWidth={3}
                name="River Level (m)"
                dot={{ fill: 'var(--color-low-risk)', r: 5 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}

export default DataAnalytics
