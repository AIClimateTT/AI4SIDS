// src/components/location-detail-sheet.tsx
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  useRealTimeConditions,
  useLocationTimeline,
} from '@/lib/hooks/useApiData'
import { dataTransformers } from '@/lib/api/client'
import type { LocationSummary } from '@/lib/api/types'
import AnalyticsModal from '@/components/analytics-modal'
import { useState } from 'react'

interface LocationDetailSheetProps {
  location: LocationSummary | null
  isOpen: boolean
  onClose: () => void
}
export function LocationDetailSheet({
  location,
  isOpen,
  onClose,
}: LocationDetailSheetProps) {
  const [analyticsOpen, setAnalyticsOpen] = useState(false)

  const {
    data: realTimeData,
    isLoading: realTimeLoading,
    error: realTimeError,
  } = useRealTimeConditions(location?.name || null, isOpen && !!location)

  const {
    data: timelineData,
    isLoading: timelineLoading,
    error: timelineError,
  } = useLocationTimeline(location?.name || null, 5, isOpen && !!location)

  if (!location) return null

  const getRiskLevelColor = (riskLevel: string) => {
    const level = riskLevel.toLowerCase()
    switch (level) {
      case 'low':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'critical':
        return 'bg-red-600 text-white'
      case 'elevated':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }
  const getTrendIcon = (trend: string) => {
    switch (trend.toLowerCase()) {
      case 'rising':
        return '📈'
      case 'falling':
        return '📉'
      case 'stable':
        return '➡️'
      default:
        return '❓'
    }
  }

  const getSentimentIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'highly negative':
        return '😰'
      case 'negative':
        return '😟'
      case 'neutral':
        return '😐'
      default:
        return '🤔'
    }
  }

  return (
    <Sheet open={isOpen} onOpenChange={onClose} modal={false}>
      <SheetContent className="w-[300px] sm:w-[350px] md:w-[400px] lg:w-[450px] xl:w-[500px] 2xl:w-[600px] max-w-[90vw] overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <span className="text-2xl">📍</span>
            {location.name}
          </SheetTitle>
          <SheetDescription>
            Real-time flood monitoring and conditions
          </SheetDescription>
          <div className="flex gap-2 pt-2">
            <Button
              onClick={() => setAnalyticsOpen(true)}
              size="sm"
              variant="outline"
              className="w-full"
            >
              📊 View Analytics & Predictions
            </Button>
          </div>
        </SheetHeader>

        <div className="space-y-6 mt-6 px-4">
          {/* Loading States */}
          {(realTimeLoading || timelineLoading) && (
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">
                    Loading real-time data...
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
          {/* Error States */}
          {(realTimeError || timelineError) && (
            <Card>
              <CardContent className="p-6">
                <div className="text-center text-red-600">
                  <div className="text-2xl mb-2">⚠️</div>
                  <p className="font-medium">Failed to load location data</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {realTimeError?.message ||
                      timelineError?.message ||
                      'Unknown error'}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
          {/* Basic Location Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Location Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Coordinates</p>
                  <p className="font-medium">
                    {location.latitude.toFixed(4)},{' '}
                    {location.longitude.toFixed(4)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Current Risk Level</p>
                  <Badge
                    className={getRiskLevelColor(
                      location.flood_risk.toLowerCase(),
                    )}
                  >
                    {location.flood_risk}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Sensor ID</p>
                  <p className="font-medium">{location.sensor_id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">River Level</p>
                  <p className="font-medium text-blue-600">
                    {location.river_level.toFixed(2)}m
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Change Rate</p>
                  <p
                    className={`font-medium ${location.change_rate > 0 ? 'text-red-600' : location.change_rate < 0 ? 'text-green-600' : 'text-gray-600'}`}
                  >
                    {location.change_rate > 0 ? '+' : ''}
                    {location.change_rate.toFixed(3)}m/15min
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Last Updated</p>
                  <p className="font-medium text-purple-600">
                    {dataTransformers.formatRelativeTime(location.last_updated)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>{' '}
          {/* Real-time Conditions */}
          {realTimeData && (
            <>
              {/* River Conditions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    🌊 River Conditions
                    <Badge
                      className={getRiskLevelColor(
                        realTimeData.river_conditions.flood_risk,
                      )}
                    >
                      {realTimeData.river_conditions.flood_risk}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Water Level</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {realTimeData.river_conditions.level.toFixed(2)}m
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Trend</p>
                      <p className="text-lg font-medium flex items-center gap-1">
                        {getTrendIcon(realTimeData.river_conditions.trend)}
                        {realTimeData.river_conditions.trend}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Change Rate</p>
                      <p className="font-medium">
                        {realTimeData.river_conditions.change_rate > 0
                          ? '+'
                          : ''}
                        {realTimeData.river_conditions.change_rate.toFixed(3)}
                        m/15min
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Sensor</p>
                      <p className="font-medium">
                        {realTimeData.river_conditions.sensor_id}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Weather Conditions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">
                    🌤️ Weather Conditions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Rainfall (15min)</p>
                      <p className="text-xl font-bold text-blue-600">
                        {realTimeData.weather.rainfall_mm.toFixed(1)}mm
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">
                        Rainfall Rate (hourly)
                      </p>
                      <p className="text-xl font-bold text-blue-500">
                        {realTimeData.weather.rainfall_rate_hourly.toFixed(1)}
                        mm/hr
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Temperature</p>
                      <p className="font-medium">
                        {realTimeData.weather.temperature_c.toFixed(1)}°C
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Humidity</p>
                      <p className="font-medium">
                        {realTimeData.weather.humidity_percent}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Social Activity */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    📱 Social Media Activity
                    <Badge variant="outline">
                      {realTimeData.social_activity.activity_level}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600">Posts Count</p>
                      <p className="text-xl font-bold">
                        {realTimeData.social_activity.post_count}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Sentiment</p>
                      <p className="font-medium flex items-center gap-1">
                        {getSentimentIcon(
                          realTimeData.social_activity.sentiment_level,
                        )}
                        {realTimeData.social_activity.sentiment_level}
                      </p>
                    </div>
                  </div>

                  {/* Recent Posts */}
                  {realTimeData.social_activity.recent_posts.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-600 mb-2">
                        Recent Posts:
                      </p>
                      <div className="space-y-2">
                        {realTimeData.social_activity.recent_posts
                          .slice(0, 3)
                          .map((post, index) => (
                            <div
                              key={index}
                              className="bg-gray-50 p-2 rounded text-sm"
                            >
                              "{post}"
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* AI Insights */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">🤖 AI Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-600 font-medium">
                        Summary
                      </p>
                      <p className="text-sm">{realTimeData.insights.summary}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 font-medium">
                        Recommendation
                      </p>
                      <p className="text-sm bg-blue-50 p-2 rounded border-l-4 border-blue-500">
                        {realTimeData.insights.recommendation}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 font-medium">
                        Correlation Analysis
                      </p>
                      <p className="text-sm">
                        {realTimeData.insights.correlation}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
          {/* Timeline Data */}
          {timelineData && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  📊 Recent Timeline (5 minutes)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Trend</p>
                      <p className="font-medium">
                        {timelineData.summary.trend}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Max Level</p>
                      <p className="font-medium">
                        {timelineData.summary.max_level.toFixed(2)}m
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Min Level</p>
                      <p className="font-medium">
                        {timelineData.summary.min_level.toFixed(2)}m
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {timelineData.timeline.slice(0, 5).map((point, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center text-sm p-2 bg-gray-50 rounded"
                    >
                      <span>
                        {dataTransformers.formatTimestamp(point.timestamp)}
                      </span>
                      <span className="font-medium">
                        {point.river_level.toFixed(2)}m
                      </span>
                      <Badge
                        size="sm"
                        className={getRiskLevelColor(point.flood_risk)}
                      >
                        {point.flood_risk}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          {/* Last Updated */}
          {realTimeData && (
            <div className="text-center text-sm text-gray-500">
              Last updated:{' '}
              {dataTransformers.formatRelativeTime(realTimeData.timestamp)}
            </div>
          )}
        </div>
      </SheetContent>

      {/* Analytics Modal */}
      {/* <AnalyticsModal
        isOpen={analyticsOpen}
        onClose={() => setAnalyticsOpen(false)}
        locationName={location.name}
      /> */}
    </Sheet>
  )
}
