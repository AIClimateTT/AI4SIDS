import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toggleTheme, initTheme, type Theme } from '@/features/shell/theme'

export function ThemeToggle() {
  const [theme, setThemeState] = useState<Theme>('light')

  useEffect(() => {
    setThemeState(initTheme())
  }, [])

  const handleToggle = () => {
    setThemeState(toggleTheme())
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleToggle}
      className="w-full justify-start gap-2 text-slate-300 hover:bg-white/10 hover:text-white"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
      {theme === 'dark' ? 'Light' : 'Dark'} mode
    </Button>
  )
}

export default ThemeToggle
