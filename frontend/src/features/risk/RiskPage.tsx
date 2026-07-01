import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BaseMap } from '@/features/shell/components/BaseMap'
import { VulnerabilityDonut } from '@/features/risk/components/VulnerabilityDonut'
import { FLOOD_RISK_MARKERS } from '@/features/risk/data'

export function RiskPage() {
  return (
    <div className="space-y-4 p-6">
      <div>
        <h2 className="text-xl font-bold">Risk &amp; Vulnerability</h2>
        <p className="text-sm text-muted-foreground">
          Across hazard categories and vulnerability
        </p>
      </div>

      <Tabs defaultValue="flood">
        <TabsList>
          <TabsTrigger value="flood">Flood Risk</TabsTrigger>
          <TabsTrigger value="landslide">Landslide Risk</TabsTrigger>
          <TabsTrigger value="heat">Heat Risk</TabsTrigger>
        </TabsList>

        <TabsContent value="flood">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Flood Risk Index</CardTitle>
              </CardHeader>
              <CardContent>
                <BaseMap markers={FLOOD_RISK_MARKERS} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Vulnerability Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <VulnerabilityDonut />
                <Button variant="link" className="px-0">
                  View Detailed Assessment →
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {['landslide', 'heat'].map((v) => (
          <TabsContent key={v} value={v}>
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                No additional data in this demo.
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}

export default RiskPage
