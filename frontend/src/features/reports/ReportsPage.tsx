import { CheckCircle2, FileText } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { SYSTEM_STATUS, REPORT_TYPES } from '@/features/reports/data'

export function ReportsPage() {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h2 className="text-xl font-bold">Reports &amp; Analytics</h2>
        <p className="text-sm text-muted-foreground">System status and report generation</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">System Status</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {SYSTEM_STATUS.map((s) => (
            <div key={s.id} className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{s.label}</span>
                <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
                  <CheckCircle2 className="mr-1 h-3 w-3" />
                  {s.status}
                </Badge>
              </div>
              <div className="mt-1 text-xs text-muted-foreground">{s.detail}</div>
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {REPORT_TYPES.map((r) => (
          <Card key={r.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <FileText className="h-5 w-5 text-blue-600" />
                {r.label}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">{r.description}</p>
              <Button size="sm" variant="outline">
                Generate
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default ReportsPage
