import { Building2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  PREPAREDNESS_RESOURCES,
  QUICK_REPORTS,
  DATA_PARTNERS,
  type ResourceLink,
} from '@/features/resources/data'

function LinkGrid({ items }: { items: ResourceLink[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {items.map(({ id, label, hint, icon: Icon }) => (
        <button
          key={id}
          className="flex flex-col items-start gap-2 rounded-lg border p-4 text-left transition-colors hover:bg-muted"
        >
          <Icon className="h-6 w-6 text-blue-600" />
          <span className="text-sm font-medium">{label}</span>
          <span className="text-xs text-blue-600">{hint}</span>
        </button>
      ))}
    </div>
  )
}

export function ResourcesPage() {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h2 className="text-xl font-bold">Resources &amp; Guidance</h2>
        <p className="text-sm text-muted-foreground">
          Preparedness materials and partner data sources
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Key Preparedness Resources</CardTitle>
        </CardHeader>
        <CardContent>
          <LinkGrid items={PREPAREDNESS_RESOURCES} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Quick Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <LinkGrid items={QUICK_REPORTS} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Data Partners</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {DATA_PARTNERS.map((p) => (
            <div
              key={p}
              className="flex flex-col items-center gap-2 rounded-lg border p-4 text-center"
            >
              <Building2 className="h-6 w-6 text-slate-500" />
              <span className="text-xs font-medium">{p}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export default ResourcesPage
