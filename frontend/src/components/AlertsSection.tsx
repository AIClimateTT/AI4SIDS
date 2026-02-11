import { useMemo, useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  AlertTriangle,
  Bell,
  Shield,
  Navigation,
  Phone,
  Loader2,
} from 'lucide-react'
import { useSystemAlerts } from '@/lib/hooks/useApiData'
import {
  generateActionItemsForLevel,
  generateAlertTitle,
  generateAlertDescription,
} from '@/lib/utils/alertActions'
import {
  getAlertStyle,
  getAlertBadge,
  mapApiRiskToComponent,
} from '@/lib/utils/riskMapping'
import { format, parseISO } from 'date-fns'

interface TransformedAlert {
  id: number
  level: string
  title: string
  location: string
  time: string
  description: string
  actions: string[]
}

const AlertsSection = () => {
  // State for showing all alerts
  const [showAllAlerts, setShowAllAlerts] = useState(false)

  // Fetch live alerts from API
  const { alerts,  criticalAlerts, highAlerts, hasAlerts } =
    useSystemAlerts()

  // Transform API alerts to component format
  const transformedAlerts: TransformedAlert[] = useMemo(() => {
    if (!alerts) return []

    return alerts.map((alert, idx) => {
      const componentLevel = mapApiRiskToComponent(alert.level.toUpperCase())

      return {
        id: idx + 1,
        level: componentLevel,
        title: generateAlertTitle(componentLevel, alert.location),
        location: alert.location,
        time: `Issued ${format(parseISO(alert.timestamp), 'HH:mm')} UTC`,
        description: generateAlertDescription(
          alert.message,
          componentLevel,
          alert.river_level,
        ),
        actions: generateActionItemsForLevel(componentLevel),
      }
    })
  }, [alerts])

  // Sort alerts by severity (critical first)
  const sortedAlerts = useMemo(() => {
    const severityOrder = { critical: 0, high: 1, moderate: 2, low: 3, safe: 4 }
    return [...transformedAlerts].sort(
      (a, b) =>
        severityOrder[a.level as keyof typeof severityOrder] -
        severityOrder[b.level as keyof typeof severityOrder],
    )
  }, [transformedAlerts])

  // Show top 3 or all alerts based on toggle state
  const activeAlerts = showAllAlerts ? sortedAlerts : sortedAlerts.slice(0, 3)

  const preparednessInfo = [
    {
      icon: Navigation,
      title: 'Evacuation Routes',
      description: 'Pre-planned safe routes to higher ground and shelters',
    },
    {
      icon: Shield,
      title: 'Emergency Shelters',
      description:
        '52 designated shelters across Trinidad and Tobago, capacity 15,000+',
    },
    {
      icon: Phone,
      title: 'Emergency Contacts',
      description: '24/7 hotlines: 110 (Emergency), 116 (Disaster Management)',
    },
  ]

 

  // No alerts state
  if (!hasAlerts) {
    return (
      <section className="py-16 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-4xl font-bold mb-3 flex items-center justify-center gap-3">
              <Bell className="h-8 w-8 text-safe" />
              Active Alerts & Notifications
            </h2>
            <p className="text-muted-foreground text-lg">
              Real-time warnings and preparedness guidance
            </p>
          </div>

          <Card className="shadow-lg border-safe/50 bg-safe/5">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Shield className="h-16 w-16 text-safe mb-4" />
              <h3 className="text-2xl font-bold text-safe mb-2">All Clear</h3>
              <p className="text-muted-foreground text-center max-w-md">
                No active flood alerts at this time. All monitored locations are
                within normal conditions.
              </p>
            </CardContent>
          </Card>

          {/* Preparedness Resources */}
          <Card className="shadow-lg mt-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-safe" />
                Preparedness Resources
              </CardTitle>
              <CardDescription>
                Essential information to stay safe during flood events
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                {preparednessInfo.map((info, idx) => (
                  <div key={idx} className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="p-3 rounded-lg bg-primary/10">
                        <info.icon className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{info.title}</h3>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {info.description}
                    </p>
                    <Button variant="outline" size="sm" className="w-full">
                      View Details
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    )
  }

  return (
    <section className="py-16 px-6">
      <div className="container mx-auto">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold mb-3 flex items-center justify-center gap-3">
            <Bell className="h-8 w-8 text-accent animate-pulse-subtle" />
            Active Alerts & Notifications
          </h2>
          <p className="text-muted-foreground text-lg">
            Real-time warnings and preparedness guidance
          </p>
          <div className="mt-4 flex gap-2 justify-center flex-wrap">
            <Badge variant="outline" className="animate-pulse-subtle">
              <div className="h-2 w-2 rounded-full bg-safe mr-2" />
              Live • Updated {format(new Date(), 'HH:mm')} UTC
            </Badge>
            {criticalAlerts.length > 0 && (
              <Badge className="bg-critical text-critical-foreground">
                {criticalAlerts.length} Critical Alert
                {criticalAlerts.length !== 1 ? 's' : ''}
              </Badge>
            )}
            {highAlerts.length > 0 && (
              <Badge className="bg-high-risk text-high-risk-foreground">
                {highAlerts.length} High Alert
                {highAlerts.length !== 1 ? 's' : ''}
              </Badge>
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {activeAlerts.map((alert) => (
            <Alert
              key={alert.id}
              className={`${getAlertStyle(alert.level as any)} border-2`}
            >
              <AlertTriangle className="h-5 w-5" />
              <AlertTitle className="flex items-center justify-between mb-2">
                <span className="font-bold">{alert.title}</span>
                <Badge className={getAlertBadge(alert.level as any)}>
                  {alert.level.toUpperCase()}
                </Badge>
              </AlertTitle>
              <AlertDescription className="space-y-3">
                <div className="text-sm ">
                  <div className="font-semibold text-foreground">
                    {alert.location}
                  </div>
                  <div className="text-muted-foreground text-xs">
                    {alert.time}
                  </div>
                </div>
                <p className="text-sm text-foreground">{alert.description}</p>
                <div className="space-y-1 text-foreground">
                  <div className="text-xs font-semibold">Action Items:</div>
                  <ul className="text-xs space-y-1">
                    {alert.actions.map((action, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-current" />
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>

        {/* Show count if more alerts exist */}
        {sortedAlerts.length > 3 && (
          <div className="text-center mb-8">
            <Button
              variant="outline"
              size="lg"
              onClick={() => setShowAllAlerts(!showAllAlerts)}
              className="text-base py-2 px-6 transition-all"
            >
              {showAllAlerts ? (
                <>
                  Show Less <span className="ml-2">▲</span>
                </>
              ) : (
                <>
                  +{sortedAlerts.length - 3} more alert
                  {sortedAlerts.length - 3 !== 1 ? 's' : ''} active{' '}
                  <span className="ml-2">▼</span>
                </>
              )}
            </Button>
          </div>
        )}

        {/* Preparedness Resources */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-safe" />
              Preparedness Resources
            </CardTitle>
            <CardDescription>
              Essential information to stay safe during flood events
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              {preparednessInfo.map((info, idx) => (
                <div key={idx} className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-lg bg-primary/10">
                      <info.icon className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{info.title}</h3>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {info.description}
                  </p>
                  <Button variant="outline" size="sm" className="w-full">
                    View Details
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  )
}

export default AlertsSection
