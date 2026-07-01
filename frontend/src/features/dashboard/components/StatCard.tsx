import { Card, CardContent } from '@/components/ui/card'
import type { Stat } from '@/features/dashboard/data'

export function StatCard({ stat }: { stat: Stat }) {
  return (
    <Card>
      <CardContent className="py-4">
        <div className="text-xs font-medium text-muted-foreground">{stat.label}</div>
        <div className="mt-1 text-2xl font-bold">{stat.value}</div>
        {stat.hint ? (
          <div className="mt-1 text-xs text-blue-600">{stat.hint}</div>
        ) : null}
      </CardContent>
    </Card>
  )
}

export default StatCard
