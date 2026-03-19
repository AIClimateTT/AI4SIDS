import { createFileRoute, Outlet, useNavigate, redirect } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { LogOut, BarChart3 } from 'lucide-react'
import { useAuth } from '@/lib/auth/AuthContext'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: () => {
    const token = localStorage.getItem('ai4sids_token')
    if (!token) {
      throw redirect({ to: '/' })
    }
  },
  component: RouteComponent,
})

function RouteComponent() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate({ to: '/' })
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-card">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-6 w-6 text-primary" />
            <div>
              <h1 className="text-xl font-bold">AI4SIDS Analytics Dashboard</h1>
              <p className="text-xs text-muted-foreground">
                Advanced Flood Risk Analysis & Monitoring
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">Research Access</p>
              <p className="text-xs text-muted-foreground">Authenticated User</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1">
        <Outlet />
      </div>
    </div>
  )
}
