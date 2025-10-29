// src/types/index.tsx

export type FloodLocation = {
  name: string
  lat: number
  lng: number
  riskLevel: 'low' | 'moderate' | 'high' | 'critical' | 'safe'
  // Enhanced fields from API integration
  sensor_id?: string
  has_data?: boolean
  api_risk_level?: string
}

// Add these to your existing types
export type SidebarProps = {
  onLocationSelect: (location: LocationSummary) => void
  selectedLocation: LocationSummary | null
}

export type Message = {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

export type ChatInterfaceProps = {
  isExpanded?: boolean
  onToggleExpand?: () => void
  selectedLocation?: LocationSummary | null
}

// Import LocationSummary from API types
import type { LocationSummary } from '@/lib/api/types'
