import type { MapMarker } from '@/features/shell/components/BaseMap'

export interface Stat {
  id: string
  label: string
  value: string
  hint?: string
}

export const STATS: Stat[] = [
  { id: 'risk', label: 'Risk Level', value: 'Moderate', hint: 'as of yesterday' },
  { id: 'alerts', label: 'Active Alerts', value: '2', hint: 'View alerts' },
  { id: 'areas', label: 'Affected Areas', value: '5', hint: 'communities' },
  { id: 'pop', label: 'Population at Risk', value: '24,560' },
  { id: 'shelters', label: 'Shelters Ready', value: '18', hint: 'View shelters' },
]

export const RISK_MARKERS: MapMarker[] = [
  { id: 'pos', label: 'Port of Spain', lat: 10.66, lng: -61.51, color: '#f59e0b', value: 'Moderate' },
  { id: 'arima', label: 'Arima', lat: 10.64, lng: -61.28, color: '#ef4444', value: 'High' },
  { id: 'sando', label: 'San Fernando', lat: 10.28, lng: -61.47, color: '#22c55e', value: 'Low' },
  { id: 'sangre', label: 'Sangre Grande', lat: 10.59, lng: -61.13, color: '#f59e0b', value: 'Moderate' },
  { id: 'tobago', label: 'Tobago', lat: 11.18, lng: -60.74, color: '#22c55e', value: 'Low' },
]

export interface WeatherSummary {
  place: string
  temperatureC: number
  condition: string
  windKmh: number
  humidityPct: number
  rainfallMm: number
}

export const WEATHER: WeatherSummary = {
  place: 'Port of Spain',
  temperatureC: 29,
  condition: 'Partly Cloudy',
  windKmh: 18,
  humidityPct: 78,
  rainfallMm: 12.4,
}

export interface UpcomingEvent {
  id: string
  title: string
  date: string
  tag: string
}

export const UPCOMING_EVENTS: UpcomingEvent[] = [
  { id: 'e1', title: 'Heavy Rainfall Watch', date: 'May 21, 2025', tag: 'Watch' },
  { id: 'e2', title: 'High Tide Advisory', date: 'May 22, 2025', tag: 'Advisory' },
]
