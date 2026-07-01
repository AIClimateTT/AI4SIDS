import { Construction } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

export function ComingSoonPage({ title }: { title: string }) {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <Card className="max-w-md text-center">
        <CardContent className="flex flex-col items-center gap-3 py-12">
          <Construction className="h-10 w-10 text-muted-foreground" />
          <h2 className="text-xl font-semibold">{title}</h2>
          <p className="text-sm text-muted-foreground">
            This section is coming soon.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default ComingSoonPage
