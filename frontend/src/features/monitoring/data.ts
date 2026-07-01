import type { MapMarker } from '@/features/shell/components/BaseMap'

export interface RainfallStation {
  id: string
  name: string
  mm: number
  lat: number
  lng: number
}

export const RAINFALL_STATIONS: RainfallStation[] = [
  { id: 'arima', name: 'Arima', mm: 23.6, lat: 10.64, lng: -61.28 },
  { id: 'sangre', name: 'Sangre Grande', mm: 16.3, lat: 10.59, lng: -61.13 },
  { id: 'tunapuna', name: 'Tunapuna', mm: 12.8, lat: 10.65, lng: -61.39 },
  { id: 'sando', name: 'San Fernando', mm: 8.4, lat: 10.28, lng: -61.47 },
  { id: 'pos', name: 'Port of Spain', mm: 5.2, lat: 10.66, lng: -61.51 },
  { id: 'mayaro', name: 'Mayaro', mm: 3.8, lat: 10.29, lng: -61.0 },
  { id: 'tobago', name: 'Tobago', mm: 2.1, lat: 11.18, lng: -60.74 },
]

// Green→amber→red by rainfall amount.
export function rainfallColor(mm: number): string {
  if (mm >= 16) return '#ef4444'
  if (mm >= 8) return '#f59e0b'
  return '#22c55e'
}

export const RAINFALL_MARKERS: MapMarker[] = RAINFALL_STATIONS.map((s) => ({
  id: s.id,
  label: s.name,
  lat: s.lat,
  lng: s.lng,
  color: rainfallColor(s.mm),
  value: `${s.mm} mm`,
}))
