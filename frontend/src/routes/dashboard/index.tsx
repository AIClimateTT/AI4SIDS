import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Bell, Activity, Radio } from 'lucide-react'
import SidebarWithSparklines from '@/components/sidebar-with-sparklines'
import DataAnalytics from '@/components/DataAnalytics'
import { LocationDetailSheet } from '@/components/location-detail-sheet'
import { AIChatBotWithButton } from '@/components/AIChatbot'
import { useSystemUpdate, useSystemAlerts } from '@/lib/hooks/useApiData'
import type { LocationSummary } from '@/lib/api/types'

export const Route = createFileRoute('/dashboard/')({
  component: RouteComponent,
})

function RouteComponent() {
  const [selectedLocation, setSelectedLocation] =
    useState<LocationSummary | null>(null)
  const [isDetailSheetOpen, setIsDetailSheetOpen] = useState(false)

  // Fetch system data for overview cards
  const { data: systemData } = useSystemUpdate()
  const { alerts, criticalAlerts, highAlerts } = useSystemAlerts()
  const totalAlerts = alerts.length

  const handleLocationSelect = (location: LocationSummary) => {
    setSelectedLocation(location)
    setIsDetailSheetOpen(true)
  }

  const handleCloseDetailSheet = () => {
    setIsDetailSheetOpen(false)
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Location List with Sparklines */}
        <div className=" border-r bg-card overflow-y-auto">
          <SidebarWithSparklines
            onLocationSelect={handleLocationSelect}
            selectedLocation={selectedLocation}
          />
        </div>

        {/* Right: Main Dashboard Content */}
        <div className="flex-1 flex flex-col overflow-auto">
          {/* Top: System Overview Cards */}
          <div className="p-6 border-b bg-muted/30">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Active Alerts Card */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Active Alerts
                  </CardTitle>
                  <Bell className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{totalAlerts}</div>
                  <div className="flex gap-2 mt-2">
                    <Badge variant="default" className="text-xs bg-red-500">
                      {criticalAlerts.length} Critical
                    </Badge>
                    <Badge variant="default" className="text-xs bg-orange-500">
                      {highAlerts.length} High
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Active Sensors Card */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Active Sensors
                  </CardTitle>
                  <Radio className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {systemData?.system_status?.active_sensors || 0}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    All systems operational
                  </p>
                </CardContent>
              </Card>

              {/* System Status Card */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Data Cycle
                  </CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {systemData?.system_status?.next_update_seconds || 0}s
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Next update in{' '}
                    {systemData?.system_status?.next_update_seconds || 0}{' '}
                    seconds
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Main: Data Analytics */}
          <div className="">
            <DataAnalytics />
          </div>
        </div>
      </div>

      {/* Location Detail Sheet (Timeline, Social Media, Predictions) */}
      <LocationDetailSheet
        location={selectedLocation}
        isOpen={isDetailSheetOpen}
        onClose={handleCloseDetailSheet}
      />

      {/* AI Chatbot (Floating) */}
      <div className="fixed bottom-6 right-6 z-50">
        <AIChatBotWithButton />
      </div>
    </div>
  )
}
