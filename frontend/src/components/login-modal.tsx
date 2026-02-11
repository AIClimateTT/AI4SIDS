import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Lock, Mail, AlertCircle, BarChart3 } from 'lucide-react'

// Demo credentials (hardcoded for demo purposes)
const DEMO_CREDENTIALS = {
  email: 'researcher@ai4sids.org',
  password: 'demo2024',
}

interface LoginModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function LoginModal({ open, onOpenChange }: LoginModalProps) {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    // Simulate network delay for realism
    await new Promise((resolve) => setTimeout(resolve, 800))

    if (
      email === DEMO_CREDENTIALS.email &&
      password === DEMO_CREDENTIALS.password
    ) {
      // Store auth state (in a real app, this would be a token)
      localStorage.setItem('ai4sids_auth', 'true')

      // Close modal and navigate to dashboard
      onOpenChange(false)
      navigate({ to: '/dashboard' })
    } else {
      setError(
        'Invalid email or password. Please try the demo credentials below.',
      )
      setIsLoading(false)
    }
  }

  const fillDemoCredentials = () => {
    setEmail(DEMO_CREDENTIALS.email)
    setPassword(DEMO_CREDENTIALS.password)
    setError('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <BarChart3 className="h-6 w-6 text-primary" />
            Advanced Analytics Access
          </DialogTitle>
          <DialogDescription>
            Log in to access real-time predictions, detailed analytics, and
            advanced flood monitoring tools.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleLogin} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="flex items-center gap-2">
              <Mail className="h-4 w-4" />
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="researcher@ai4sids.org"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="flex items-center gap-2">
              <Lock className="h-4 w-4" />
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Demo credentials helper */}
          <div className="bg-muted p-3 rounded-md border">
            <div className="text-sm font-medium mb-2">Demo Access:</div>
            <div className="text-xs space-y-1 text-muted-foreground">
              <div>
                <strong>Email:</strong> {DEMO_CREDENTIALS.email}
              </div>
              <div>
                <strong>Password:</strong> {DEMO_CREDENTIALS.password}
              </div>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="mt-2 w-full"
              onClick={fillDemoCredentials}
              disabled={isLoading}
            >
              Fill Demo Credentials
            </Button>
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Logging in...
              </>
            ) : (
              'Access Dashboard'
            )}
          </Button>
        </form>

        <div className="text-xs text-center text-muted-foreground mt-4 pt-4 border-t">
          For research access, contact{' '}
          <a
            href="https://climate.lab.tt/index.php/contact-us"
            target="_blank"
            className="text-primary hover:underline"
          >
            ClimeLab TT
          </a>
        </div>
      </DialogContent>
    </Dialog>
  )
}
