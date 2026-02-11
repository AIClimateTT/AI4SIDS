import { useState } from 'react'
import { Shield, Menu, Globe } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { LoginModal } from '@/components/login-modal'

const Header = () => {
  const [loginOpen, setLoginOpen] = useState(false)

  return (
    <>
      <LoginModal open={loginOpen} onOpenChange={setLoginOpen} />
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <img
              src={'logo-icon.png'}
              alt="AI4SIDS Logo"
              className="h-10 w-10"
            />
            <div>
              <h1 className="text-lg font-bold text-primary">AI4SIDS</h1>
              <p className="text-xs text-muted-foreground">
                Disaster Resilience Dashboard
              </p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <a
              href="#dashboard"
              className="text-sm font-medium hover:text-primary transition-smooth"
            >
              Dashboard
            </a>
            <a
              href="#forecast"
              className="text-sm font-medium hover:text-primary transition-smooth"
            >
              Forecast
            </a>
            <a
              href="#alerts"
              className="text-sm font-medium hover:text-primary transition-smooth"
            >
              Alerts
            </a>
            <a
              href="#assistant"
              className="text-sm font-medium hover:text-primary transition-smooth"
            >
              AI Assistant
            </a>
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {/* Language Selector */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <Globe className="h-4 w-4 mr-2" />
                  EN
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>English</DropdownMenuItem>
                <DropdownMenuItem>Español</DropdownMenuItem>
                <DropdownMenuItem>Français</DropdownMenuItem>
                <DropdownMenuItem>Nederlands</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Emergency Button */}
            <Button className="bg-critical hover:bg-critical/90 shadow-alert hidden sm:flex">
              <Shield className="h-4 w-4 mr-2" />
              Emergency
            </Button>

            {/* Login */}
            <Button
              variant="outline"
              className="hidden md:flex"
              onClick={() => setLoginOpen(true)}
            >
              Log in
            </Button>

            {/* Mobile Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild className="md:hidden">
                <Button variant="ghost" size="sm">
                  <Menu className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem asChild>
                  <a href="#dashboard">Dashboard</a>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <a href="#forecast">Forecast</a>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <a href="#alerts">Alerts</a>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <a href="#assistant">AI Assistant</a>
                </DropdownMenuItem>
                <DropdownMenuItem className="text-critical">
                  <Shield className="h-4 w-4 mr-2" />
                  Emergency
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setLoginOpen(true)}
                  >
                    Log in
                  </Button>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>
    </>
  )
}

export default Header
