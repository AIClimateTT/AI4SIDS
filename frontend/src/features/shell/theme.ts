export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'ai4sids_theme'

export function getStoredTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored === 'dark' ? 'dark' : 'light'
}

export function applyTheme(theme: Theme): void {
  document.documentElement.classList.toggle('dark', theme === 'dark')
}

export function setTheme(theme: Theme): void {
  localStorage.setItem(STORAGE_KEY, theme)
  applyTheme(theme)
}

export function toggleTheme(): Theme {
  const next: Theme = getStoredTheme() === 'dark' ? 'light' : 'dark'
  setTheme(next)
  return next
}

export function initTheme(): Theme {
  const theme = getStoredTheme()
  applyTheme(theme)
  return theme
}
