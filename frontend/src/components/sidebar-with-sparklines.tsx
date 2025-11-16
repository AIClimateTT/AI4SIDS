// src/components/sidebar-with-sparklines.tsx
import React, { useState, useMemo } from 'react'
import type { SidebarProps } from '@/lib/types'
import {
  useSystemUpdate,
  useSystemStatus,
  useSystemAlerts,
  useDataFreshness,
} from '@/lib/hooks/useApiData'
import { dataTransformers } from '@/lib/api/client'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import SparklineCard from '@/components/sparkline-card'


// Enhanced sidebar with sparklines
const SidebarWithSparklines: React.FC<SidebarProps> = ({
  onLocationSelect,
  selectedLocation,
}) => {
 
  const [showAlerts, setShowAlerts] = useState(true)
  const [expandedSections, setExpandedSections] = useState<{
    [key: string]: boolean
  }>({
    critical: true,
    high: true,
    moderate: false,
    low: false,
    safe: false,
  })

  // API data hooks
  const {
    data: systemUpdate,
    isLoading: systemLoading,
    error: systemError,
  } = useSystemUpdate()
  const {
    dataCycleProgress,
  } = useSystemStatus()
  const { alerts, hasAlerts } = useSystemAlerts()
  const { systemUpdateFreshness } = useDataFreshness()

  // Extract and process locations
  const locations = systemUpdate?.locations || []

  // Group locations by risk level
  const groupedLocations = useMemo(
    () => ({
      critical: locations.filter((loc) => loc.flood_risk === 'CRITICAL'),
      high: locations.filter((loc) => loc.flood_risk === 'HIGH'),
      moderate: locations.filter((loc) => loc.flood_risk === 'MODERATE'),
      low: locations.filter((loc) => loc.flood_risk === 'LOW'),
      safe: locations.filter((loc) => loc.flood_risk === 'SAFE'),
    }),
    [locations],
  )

  // Toggle section expansion
  const toggleSection = (
    section: 'critical' | 'high' | 'moderate' | 'low' | 'safe',
  ) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }
  // Loading state
  if (systemLoading) {
    return (
      <div className="w-[420px] bg-white border-r border-gray-300 shadow-lg h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading system data...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (systemError) {
    return (
      <div className="w-[420px] bg-white border-r border-gray-300 shadow-lg h-full flex items-center justify-center">
        <div className="text-center p-4">
          <div className="text-red-500 text-2xl mb-2">⚠️</div>
          <p className="text-red-600 font-medium">Failed to load system data</p>
          <p className="text-gray-600 text-sm mt-1">
            Please check API connection
          </p>
        </div>
      </div>
    )
  }


  return (
    <div className="w-[420px] bg-gray-50 border-r border-gray-300 shadow-lg h-full overflow-y-auto flex flex-col">
     

      {/* Alerts Section */}
      {showAlerts && hasAlerts && (
        <div className="p-4 bg-white border-b border-gray-200 shrink-0">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-800">
              Active Alerts
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAlerts(false)}
              className="h-6 w-6 p-0 hover:bg-gray-100"
            >
              ×
            </Button>
          </div>

          <div className="space-y-2 max-h-40 overflow-y-auto">
            {alerts.slice(0, 3).map((alert, index) => {
              const styling = dataTransformers.getAlertStyling(alert.level)
              return (
                <div
                  key={index}
                  className={`p-2 rounded-md border text-xs ${styling.bgColor} ${styling.textColor} ${styling.borderColor}`}
                >
                  <div className="flex items-start space-x-2">
                    <span className="text-base">{styling.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">
                        {alert.location}
                      </div>
                      <div className="text-xs opacity-75 line-clamp-2">
                        {alert.message}
                      </div>
                      <div className="text-xs opacity-60 mt-1">
                        {dataTransformers.formatRelativeTime(alert.timestamp)}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Locations with Sparklines */}
      <div className="flex-1 p-4 space-y-4 overflow-y-auto">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-800">
            Monitored Locations
          </h3>
          <Badge variant="outline" className="text-xs">
            {locations.length} total
          </Badge>
        </div>

        {/* CRITICAL Section */}
        {groupedLocations.critical.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={() => toggleSection('critical')}
              className="w-full flex items-center justify-between px-3 py-2 bg-critical/10 border border-critical/30 rounded-lg hover:bg-critical/20 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <span className="text-critical font-bold">🔴 CRITICAL</span>
                <Badge className="bg-critical text-critical-foreground text-xs">
                  {groupedLocations.critical.length}
                </Badge>
              </div>
              <span className="text-critical text-sm">
                {expandedSections.critical ? '▼' : '▶'}
              </span>
            </button>
            {expandedSections.critical && (
              <div className="space-y-2 pl-2">
                {groupedLocations.critical.map((location) => (
                  <SparklineCard
                    key={location.name}
                    locationName={location.name}
                    riskLevel={location.flood_risk}
                    currentValue={location.river_level}
                    changeRate={location.change_rate}
                    onSelect={() => onLocationSelect(location)}
                    enabled={true} // Always enabled for critical
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* HIGH Section */}
        {groupedLocations.high.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={() => toggleSection('high')}
              className="w-full flex items-center justify-between px-3 py-2 bg-high-risk/10 border border-high-risk/30 rounded-lg hover:bg-high-risk/20 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <span className="text-high-risk font-bold">🟠 HIGH</span>
                <Badge className="bg-high-risk text-high-risk-foreground text-xs">
                  {groupedLocations.high.length}
                </Badge>
              </div>
              <span className="text-high-risk text-sm">
                {expandedSections.high ? '▼' : '▶'}
              </span>
            </button>
            {expandedSections.high && (
              <div className="space-y-2 pl-2">
                {groupedLocations.high.map((location) => (
                  <SparklineCard
                    key={location.name}
                    locationName={location.name}
                    riskLevel={location.flood_risk}
                    currentValue={location.river_level}
                    changeRate={location.change_rate}
                    onSelect={() => onLocationSelect(location)}
                    enabled={true} // Always enabled for high risk
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* MODERATE Section */}
        {groupedLocations.moderate.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={() => toggleSection('moderate')}
              className="w-full flex items-center justify-between px-3 py-2 bg-moderate/10 border border-moderate/30 rounded-lg hover:bg-moderate/20 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <span className="text-moderate font-bold">🟡 MODERATE</span>
                <Badge className="bg-moderate text-moderate-foreground text-xs">
                  {groupedLocations.moderate.length}
                </Badge>
              </div>
              <span className="text-moderate text-sm">
                {expandedSections.moderate ? '▼' : '▶'}
              </span>
            </button>
            {expandedSections.moderate && (
              <div className="space-y-2 pl-2">
                {groupedLocations.moderate.map((location) => (
                  <SparklineCard
                    key={location.name}
                    locationName={location.name}
                    riskLevel={location.flood_risk}
                    currentValue={location.river_level}
                    changeRate={location.change_rate}
                    onSelect={() => onLocationSelect(location)}
                    enabled={expandedSections.moderate} // Only enabled when expanded
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* LOW Section */}
        {groupedLocations.low.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={() => toggleSection('low')}
              className="w-full flex items-center justify-between px-3 py-2 bg-low-risk/10 border border-low-risk/30 rounded-lg hover:bg-low-risk/20 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <span className="text-low-risk font-bold">� LOW</span>
                <Badge className="bg-low-risk text-low-risk-foreground text-xs">
                  {groupedLocations.low.length}
                </Badge>
              </div>
              <span className="text-low-risk text-sm">
                {expandedSections.low ? '▼' : '▶'}
              </span>
            </button>
            {expandedSections.low && (
              <div className="space-y-2 pl-2">
                {groupedLocations.low.map((location) => (
                  <SparklineCard
                    key={location.name}
                    locationName={location.name}
                    riskLevel={location.flood_risk}
                    currentValue={location.river_level}
                    changeRate={location.change_rate}
                    onSelect={() => onLocationSelect(location)}
                    enabled={expandedSections.low} // Only enabled when expanded
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* SAFE Section */}
        {groupedLocations.safe.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={() => toggleSection('safe')}
              className="w-full flex items-center justify-between px-3 py-2 bg-safe/10 border border-safe/30 rounded-lg hover:bg-safe/20 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <span className="text-safe font-bold">🟢 SAFE</span>
                <Badge className="bg-safe text-safe-foreground text-xs">
                  {groupedLocations.safe.length}
                </Badge>
              </div>
              <span className="text-safe text-sm">
                {expandedSections.safe ? '▼' : '▶'}
              </span>
            </button>
            {expandedSections.safe && (
              <div className="space-y-2 pl-2">
                {groupedLocations.safe.map((location) => (
                  <SparklineCard
                    key={location.name}
                    locationName={location.name}
                    riskLevel={location.flood_risk}
                    currentValue={location.river_level}
                    changeRate={location.change_rate}
                    onSelect={() => onLocationSelect(location)}
                    enabled={expandedSections.safe} // Only enabled when expanded
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {locations.length === 0 && (
          <div className="text-center text-gray-500 py-12">
            <div className="text-4xl mb-3">📍</div>
            <p className="font-medium">No locations available</p>
            <p className="text-sm mt-1">Check API connection</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 bg-white p-4 flex-shrink-0">
        <div className="text-xs text-gray-500 space-y-1">
          <div className="flex justify-between">
            <span>System Update:</span>
            <span className="font-medium">{systemUpdateFreshness}</span>
          </div>
          <div className="flex justify-between">
            <span>Data Cycle:</span>
            <span className="font-medium">{dataCycleProgress}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SidebarWithSparklines
