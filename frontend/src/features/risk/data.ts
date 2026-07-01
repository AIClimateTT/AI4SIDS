import type { MapMarker } from '@/features/shell/components/BaseMap'

export interface VulnerabilitySlice {
  label: string
  value: number
  color: string
}

// Total communities = 82.
export const VULNERABILITY: VulnerabilitySlice[] = [
  { label: 'Very High', value: 14, color: '#dc2626' },
  { label: 'High', value: 26, color: '#f97316' },
  { label: 'Moderate', value: 24, color: '#f59e0b' },
  { label: 'Low', value: 9, color: '#3b82f6' },
  { label: 'Very Low', value: 9, color: '#22c55e' },
]

export const TOTAL_COMMUNITIES = VULNERABILITY.reduce((sum, s) => sum + s.value, 0)

export const FLOOD_RISK_MARKERS: MapMarker[] = [
  { id: 'pos', label: 'Port of Spain', lat: 10.66, lng: -61.51, color: '#f59e0b', value: 'Moderate' },
  { id: 'arima', label: 'Arima', lat: 10.64, lng: -61.28, color: '#dc2626', value: 'Very High' },
  { id: 'caroni', label: 'Caroni Basin', lat: 10.5, lng: -61.4, color: '#f97316', value: 'High' },
  { id: 'sando', label: 'San Fernando', lat: 10.28, lng: -61.47, color: '#3b82f6', value: 'Low' },
  { id: 'tobago', label: 'Tobago', lat: 11.18, lng: -60.74, color: '#22c55e', value: 'Very Low' },
]
