// src/components/sparkline-card.tsx
import React from 'react'
import {
  Sparklines,
  SparklinesLine,
  SparklinesReferenceLine,
} from 'react-sparklines'
import { useLocationHistory } from '@/lib/hooks/useApiData'

interface SparklineCardProps {
  locationName: string
  riskLevel: 'LOW' | 'ELEVATED' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  currentValue: number
  changeRate: number
  onSelect?: () => void
  enabled?: boolean // Enable/disable query
  dataPoints?: number // Number of history points to fetch
}

const SparklineCard: React.FC<SparklineCardProps> = ({
  locationName,
  riskLevel,
  currentValue,
  changeRate,
  onSelect,
  enabled = true,
  dataPoints = 20,
}) => {
  // Use TanStack Query for data fetching
  const {
    data: historyData,
    isLoading,
    error,
  } = useLocationHistory(locationName, dataPoints, enabled)

  // Get risk color
  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'CRITICAL':
        return 'bg-red-500'
      case 'HIGH':
        return 'bg-orange-500'
      case 'MEDIUM':
      case 'ELEVATED':
        return 'bg-yellow-500'
      case 'LOW':
        return 'bg-green-500'
      default:
        return 'bg-gray-500'
    }
  }

  // Get sparkline color based on trend
  const getSparklineColor = (): string => {
    if (!historyData) return '#3B82F6' // blue

    const { trend, current } = historyData

    // Critical/High risk + rising = red
    if (
      (current.risk === 'CRITICAL' || current.risk === 'HIGH') &&
      trend.direction === 'rising'
    ) {
      return '#EF4444' // red
    }
    // Rising = orange
    if (trend.direction === 'rising') {
      return '#F97316' // orange
    }
    // Falling = green
    if (trend.direction === 'falling') {
      return '#10B981' // green
    }
    // Stable = blue
    return '#3B82F6' // blue
  }

  // Get trend icon
  const getTrendIcon = () => {
    if (!historyData) return '→'

    const { trend } = historyData
    if (trend.direction === 'rising') return '↑'
    if (trend.direction === 'falling') return '↓'
    return '→'
  }

  // Get values for sparkline
  const sparklineValues = historyData?.history.map((point) => point.value) || []

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
        <div className="flex items-center justify-between mb-2">
          <div className="h-4 bg-gray-200 rounded w-24"></div>
          <div className="h-6 w-6 bg-gray-200 rounded-full"></div>
        </div>
        <div className="h-16 bg-gray-200 rounded mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-16"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-red-200 p-4">
        <div className="text-red-600 text-sm">
          {error instanceof Error ? error.message : 'Failed to load data'}
        </div>
      </div>
    )
  }

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border-l-4 ${getRiskColor(
        riskLevel,
      ).replace(
        'bg-',
        'border-',
      )} border-t border-r border-b border-gray-200 p-4 transition-all hover:shadow-md ${
        onSelect ? 'cursor-pointer' : ''
      }`}
      onClick={onSelect}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <h3 className="font-semibold text-gray-900 text-sm">
            {locationName}
          </h3>
          <span
            className={`w-2 h-2 rounded-full ${getRiskColor(riskLevel)}`}
            title={riskLevel}
          ></span>
        </div>
        <span className="text-xs font-medium text-gray-500 uppercase">
          {riskLevel}
        </span>
      </div>

      {/* Sparkline Chart */}
      <div className="mb-16 h-16 relative">
        {sparklineValues.length > 0 ? (
          <div className="relative group">
            <Sparklines
              data={sparklineValues}
              width={280}
              height={60}
              margin={5}
            >
              <SparklinesLine
                color={getSparklineColor()}
                style={{ strokeWidth: 2, fill: 'none' }}
              />
              {/* Reference line at flood threshold (3.0m) */}
              <SparklinesReferenceLine
                type="custom"
                value={3.0}
                style={{
                  stroke: '#DC2626',
                  strokeDasharray: '2,2',
                  strokeWidth: 1,
                }}
              />
            </Sparklines>

            {/* Axis Context Tooltip */}
            <div className="absolute -top-2 left-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
              <div className="bg-gray-900 text-white text-xs rounded px-2 py-1 mx-auto w-fit shadow-lg">
                <div className="flex flex-col space-y-1">
                  <div className="flex justify-between items-center space-x-4">
                    <span className="text-gray-300">Y-axis:</span>
                    <span>
                      River Level ({Math.min(...sparklineValues).toFixed(1)}m -{' '}
                      {Math.max(...sparklineValues).toFixed(1)}m)
                    </span>
                  </div>
                  <div className="flex justify-between items-center space-x-4">
                    <span className="text-gray-300">X-axis:</span>
                    <span>
                      Last {historyData?.history.length || 20} readings (5 min)
                    </span>
                  </div>
                  <div className="flex justify-between items-center space-x-4">
                    <span className="text-gray-300">Trend:</span>
                    <span
                      className={`${
                        getSparklineColor() === '#EF4444'
                          ? 'text-red-300'
                          : getSparklineColor() === '#F97316'
                            ? 'text-orange-300'
                            : getSparklineColor() === '#10B981'
                              ? 'text-green-300'
                              : 'text-blue-300'
                      }`}
                    >
                      {historyData?.trend.direction}{' '}
                      {historyData?.trend.percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="border-t border-gray-700 pt-1 mt-1">
                    <span className="text-red-300">
                      Red line: Flood threshold (3.0m)
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Subtle Axis Indicators */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Y-axis labels - moved inside chart area */}
              <div className="absolute left-1 top-0 text-xs text-gray-400 bg-white/80 px-1 rounded">
                {Math.max(...sparklineValues).toFixed(1)}m
              </div>
              <div className="absolute left-1 bottom-0 text-xs text-gray-400 bg-white/80 px-1 rounded">
                {Math.min(...sparklineValues).toFixed(1)}m
              </div>

              {/* X-axis labels - positioned to not overlap with content below */}
              <div className="absolute -bottom-5 left-1 text-xs text-gray-400">
                -{Math.round(((historyData?.history.length || 20) * 15) / 60)}
                min
              </div>
              <div className="absolute -bottom-5 right-1 text-xs text-gray-400">
                now
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400 text-xs">
            No data available
          </div>
        )}

        {/* Mini Legend for Context */}
        {sparklineValues.length > 0 && (
          <div className="mt-6 flex justify-between text-xs text-gray-400">
            <span>Y: River Level</span>
            <span>X: Last 5min | Red line: 3.0m threshold</span>
          </div>
        )}
      </div>

      {/* Metrics */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-lg font-bold text-gray-900">
            {currentValue.toFixed(2)}m
          </span>
          <span
            className={`text-sm font-medium ${
              changeRate > 0
                ? 'text-red-600'
                : changeRate < 0 || changeRate < 0.05
                  ? 'text-green-600'
                  : 'text-gray-600'
            }`}
          >
            {getTrendIcon()} {Math.abs(changeRate).toFixed(3)}
          </span>
        </div>

        {/* Mini stats */}
        {historyData && (
          <div className="text-xs text-gray-500">
            <span title="Trend percentage">
              {historyData.trend.percentage > 0 ? '+' : ''}
              {historyData.trend.percentage.toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {/* Optional: Show time since last update */}
      {historyData && (
        <div className="mt-2 text-xs text-gray-400">
          Updated:{' '}
          {new Date(historyData.current.timestamp).toLocaleTimeString()}
        </div>
      )}
    </div>
  )
}

export default SparklineCard
