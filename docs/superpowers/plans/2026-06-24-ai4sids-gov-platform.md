# AI4SIDS-Gov Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the authenticated `/dashboard` area with a multi-page, statically-seeded "AI4SIDS-Gov" platform matching the provided mock, organized as feature-per-page folders under `src/features/`.

**Architecture:** A reusable shell (dark sidebar + top bar + theme toggle) wraps an `<Outlet/>` at the `/dashboard` route. Each nav destination is a thin TanStack route file that mounts a page from its own `features/<name>/` folder. Every page reads typed static data from its own `data.ts`. No backend calls except the existing `useAuth().logout`.

**Tech Stack:** React 19, TanStack Router (client SPA — `tanstackStart` is disabled in `vite.config.ts`), shadcn/ui (new-york, lucide icons), Tailwind v4, react-leaflet, recharts, vitest + @testing-library/react.

## Global Constraints

- **Spec:** `docs/superpowers/specs/2026-06-24-ai4sids-gov-platform-design.md`. All seed values come from there — copy them exactly.
- **Static only:** No `fetch`/API/query hooks on any new page. The only allowed runtime data source is `useAuth()` (logout) from `@/lib/auth/AuthContext`.
- **All new code lives under** `frontend/src/features/`. Route files under `frontend/src/routes/dashboard/` stay thin wrappers (mount a feature page, nothing else).
- **Working directory for all commands:** `frontend/` (dev server: `pnpm dev` on port 3004; tests: `pnpm test`; typecheck: `pnpm exec tsc --noEmit`; build: `pnpm build`).
- **Package manager:** pnpm (repo has `pnpm-lock.yaml`).
- **shadcn install command:** `pnpm dlx shadcn@latest add <component> --yes`.
- **Imports:** use the `@/` alias (e.g. `@/components/ui/card`, `@/features/shell/nav`).
- **Icons:** `lucide-react` only.
- **Theme:** light/dark via a `dark` class toggled on `document.documentElement`, persisted in `localStorage` under key `ai4sids_theme`. The `.dark` CSS block already exists in `src/styles.css` (line ~126) and `@custom-variant dark` is defined — do NOT add new theme CSS.
- **Map center:** Trinidad & Tobago = `[10.5, -61.3]`, default zoom `9`. Tile URL: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`. Always `import 'leaflet/dist/leaflet.css'` in map components.
- **Existing risk color utility classes** (Tailwind v4 theme tokens, already defined): `bg-safe`, `bg-low-risk`, `bg-moderate`, `bg-high-risk`, `bg-critical` (each with a matching `-foreground`).
- **Commit style:** end every commit message with:
  ```
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  ```
- Current branch is `demo-3`; commit there (do not create PRs unless asked).

---

## File Structure

```
frontend/
  vite.config.ts                         # MODIFY: add vitest test config (jsdom)
  vitest.setup.ts                        # CREATE: RTL + jest-dom setup
  src/features/
    shell/
      types.ts                           # NavItem, AlertSeverity, AlertItem, StatCard types
      nav.ts                             # NAV_ITEMS array + getNavItemByPath()
      theme.ts                           # Theme get/set/toggle/init helpers
      components/
        ThemeToggle.tsx
        GovSidebar.tsx
        GovTopBar.tsx
        GovLayout.tsx
        BaseMap.tsx                      # reusable Leaflet wrapper (CircleMarkers + legend)
    placeholder/
      ComingSoonPage.tsx
    alerts/
      data.ts
      filter.ts                          # filterAlerts() pure helper
      components/AlertCard.tsx           # shared; imported by dashboard
      AlertsPage.tsx
    dashboard/
      data.ts
      components/StatCard.tsx
      components/WeatherOverviewCard.tsx
      DashboardPage.tsx
    monitoring/
      data.ts
      MonitoringPage.tsx
    risk/
      data.ts
      components/VulnerabilityDonut.tsx
      RiskPage.tsx
    assistant/
      data.ts
      AssistantPage.tsx
    resources/
      data.ts
      ResourcesPage.tsx
    reports/
      data.ts
      ReportsPage.tsx
  src/routes/dashboard/
    route.tsx                            # MODIFY: keep auth guard, swap layout to GovLayout
    index.tsx                            # MODIFY: mount DashboardPage
    monitoring.tsx                       # CREATE
    risk.tsx                             # CREATE
    alerts.tsx                           # CREATE
    assistant.tsx                        # CREATE
    resources.tsx                        # CREATE
    reports.tsx                          # CREATE
    data.tsx                             # CREATE (placeholder)
    settings.tsx                         # CREATE (placeholder)
```

`src/routeTree.gen.ts` is regenerated automatically by the TanStack Router vite plugin when `pnpm dev` runs — do not hand-edit it.

**Testing approach:** Pure-logic modules (`theme.ts`, `nav.ts`, `alerts/filter.ts`) get real TDD unit tests. Presentational components without Leaflet/recharts (`AlertCard`, `ComingSoonPage`) get RTL smoke render tests. Pages that embed Leaflet or recharts are verified by typecheck + build + manual dev-server check (jsdom cannot lay out Leaflet/recharts reliably), as listed in each task.

---

### Task 1: Wire up the test runner

**Files:**
- Modify: `frontend/vite.config.ts`
- Create: `frontend/vitest.setup.ts`
- Test: `frontend/src/features/shell/__tests__/smoke.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: a working `pnpm test` with jsdom environment and `@testing-library/jest-dom` matchers; global `expect`/`describe`/`it`.

- [ ] **Step 1: Write a failing smoke test**

Create `frontend/src/features/shell/__tests__/smoke.test.ts`:

```ts
import { describe, it, expect } from 'vitest'

describe('test runner', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2)
  })
})
```

- [ ] **Step 2: Run it to confirm the runner is not yet configured for jsdom/globals**

Run: `pnpm test`
Expected: either FAIL/erroring config OR the test runs but jsdom is not active. Proceed regardless — we are about to set the config explicitly.

- [ ] **Step 3: Add the vitest setup file**

Create `frontend/vitest.setup.ts`:

```ts
import '@testing-library/jest-dom/vitest'
```

- [ ] **Step 4: Add the `test` block to vite config**

In `frontend/vite.config.ts`, change the `defineConfig` import line and add a `test` key. Replace:

```ts
import { defineConfig } from 'vite'
```

with:

```ts
/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
```

and add this `test` property to the config object (sibling of `plugins`):

```ts
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
```

- [ ] **Step 5: Run the smoke test**

Run: `pnpm test`
Expected: PASS (1 test).

- [ ] **Step 6: Commit**

```bash
git add frontend/vite.config.ts frontend/vitest.setup.ts frontend/src/features/shell/__tests__/smoke.test.ts
git commit -m "test: configure vitest with jsdom and RTL setup

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Theme helpers + ThemeToggle

**Files:**
- Create: `frontend/src/features/shell/theme.ts`
- Create: `frontend/src/features/shell/components/ThemeToggle.tsx`
- Test: `frontend/src/features/shell/__tests__/theme.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `type Theme = 'light' | 'dark'`
  - `getStoredTheme(): Theme` (defaults to `'light'`)
  - `applyTheme(theme: Theme): void` (toggles `dark` class on `document.documentElement`)
  - `setTheme(theme: Theme): void` (persists to localStorage key `ai4sids_theme` + applies)
  - `toggleTheme(): Theme` (flips current, persists, applies, returns new value)
  - `initTheme(): Theme` (reads stored, applies, returns it)
  - default export `ThemeToggle` React component.

- [ ] **Step 1: Write failing tests**

Create `frontend/src/features/shell/__tests__/theme.test.ts`:

```ts
import { describe, it, expect, beforeEach } from 'vitest'
import {
  getStoredTheme,
  setTheme,
  toggleTheme,
  initTheme,
} from '../theme'

beforeEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove('dark')
})

describe('theme helpers', () => {
  it('defaults to light when nothing stored', () => {
    expect(getStoredTheme()).toBe('light')
  })

  it('setTheme persists and applies the dark class', () => {
    setTheme('dark')
    expect(localStorage.getItem('ai4sids_theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('setTheme light removes the dark class', () => {
    setTheme('dark')
    setTheme('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggleTheme flips and returns the new value', () => {
    setTheme('light')
    expect(toggleTheme()).toBe('dark')
    expect(getStoredTheme()).toBe('dark')
  })

  it('initTheme applies the stored theme', () => {
    localStorage.setItem('ai4sids_theme', 'dark')
    expect(initTheme()).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `pnpm test src/features/shell/__tests__/theme.test.ts`
Expected: FAIL ("Cannot find module '../theme'").

- [ ] **Step 3: Implement `theme.ts`**

Create `frontend/src/features/shell/theme.ts`:

```ts
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
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pnpm test src/features/shell/__tests__/theme.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: Implement `ThemeToggle.tsx`**

Create `frontend/src/features/shell/components/ThemeToggle.tsx`:

```tsx
import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { getStoredTheme, toggleTheme, initTheme, type Theme } from '@/features/shell/theme'

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
```

- [ ] **Step 6: Typecheck**

Run: `pnpm exec tsc --noEmit`
Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/features/shell/theme.ts frontend/src/features/shell/components/ThemeToggle.tsx frontend/src/features/shell/__tests__/theme.test.ts
git commit -m "feat(shell): add theme helpers and toggle

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Shared types + nav config

**Files:**
- Create: `frontend/src/features/shell/types.ts`
- Create: `frontend/src/features/shell/nav.ts`
- Test: `frontend/src/features/shell/__tests__/nav.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `types.ts`: `AlertSeverity = 'warning' | 'alert' | 'advisory'`; `interface AlertItem { id: string; title: string; location: string; timestamp: string; severity: AlertSeverity }`; `interface NavItem { label: string; to: string; icon: LucideIcon; badge?: number }`.
  - `nav.ts`: `NAV_ITEMS: NavItem[]` and `getNavItemByPath(pathname: string): NavItem | undefined`.

- [ ] **Step 1: Write failing test**

Create `frontend/src/features/shell/__tests__/nav.test.ts`:

```ts
import { describe, it, expect } from 'vitest'
import { NAV_ITEMS, getNavItemByPath } from '../nav'

describe('nav config', () => {
  it('has the nine nav items in order', () => {
    expect(NAV_ITEMS.map((n) => n.to)).toEqual([
      '/dashboard',
      '/dashboard/monitoring',
      '/dashboard/risk',
      '/dashboard/alerts',
      '/dashboard/assistant',
      '/dashboard/resources',
      '/dashboard/reports',
      '/dashboard/data',
      '/dashboard/settings',
    ])
  })

  it('puts a badge of 6 on alerts', () => {
    const alerts = NAV_ITEMS.find((n) => n.to === '/dashboard/alerts')
    expect(alerts?.badge).toBe(6)
  })

  it('resolves the exact path', () => {
    expect(getNavItemByPath('/dashboard/monitoring')?.label).toBe(
      'Real-time Monitoring',
    )
  })

  it('resolves dashboard index exactly without matching deeper paths', () => {
    expect(getNavItemByPath('/dashboard')?.label).toBe('Dashboard')
    expect(getNavItemByPath('/dashboard/risk')?.label).toBe(
      'Risk & Vulnerability',
    )
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `pnpm test src/features/shell/__tests__/nav.test.ts`
Expected: FAIL ("Cannot find module '../nav'").

- [ ] **Step 3: Implement `types.ts`**

Create `frontend/src/features/shell/types.ts`:

```ts
import type { LucideIcon } from 'lucide-react'

export type AlertSeverity = 'warning' | 'alert' | 'advisory'

export interface AlertItem {
  id: string
  title: string
  location: string
  timestamp: string
  severity: AlertSeverity
}

export interface NavItem {
  label: string
  to: string
  icon: LucideIcon
  badge?: number
}
```

- [ ] **Step 4: Implement `nav.ts`**

Create `frontend/src/features/shell/nav.ts`:

```ts
import {
  LayoutDashboard,
  Radio,
  ShieldAlert,
  Bell,
  Bot,
  BookOpen,
  BarChart3,
  Database,
  Settings,
} from 'lucide-react'
import type { NavItem } from '@/features/shell/types'

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Real-time Monitoring', to: '/dashboard/monitoring', icon: Radio },
  { label: 'Risk & Vulnerability', to: '/dashboard/risk', icon: ShieldAlert },
  { label: 'Alerts & Notifications', to: '/dashboard/alerts', icon: Bell, badge: 6 },
  { label: 'AI Preparedness Assistant', to: '/dashboard/assistant', icon: Bot },
  { label: 'Resources & Guidance', to: '/dashboard/resources', icon: BookOpen },
  { label: 'Reports & Analytics', to: '/dashboard/reports', icon: BarChart3 },
  { label: 'Data Management', to: '/dashboard/data', icon: Database },
  { label: 'Settings', to: '/dashboard/settings', icon: Settings },
]

export function getNavItemByPath(pathname: string): NavItem | undefined {
  // Strip trailing slash (except root) for stable exact matching.
  const path = pathname.length > 1 ? pathname.replace(/\/$/, '') : pathname
  return NAV_ITEMS.find((item) => item.to === path)
}
```

- [ ] **Step 5: Run tests to verify pass**

Run: `pnpm test src/features/shell/__tests__/nav.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/shell/types.ts frontend/src/features/shell/nav.ts frontend/src/features/shell/__tests__/nav.test.ts
git commit -m "feat(shell): add shared types and nav config

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: GovSidebar

**Files:**
- Create: `frontend/src/features/shell/components/GovSidebar.tsx`
- Test: `frontend/src/features/shell/__tests__/GovSidebar.test.tsx`

**Interfaces:**
- Consumes: `NAV_ITEMS` (Task 3), `ThemeToggle` (Task 2).
- Produces: named export `GovSidebar` (no props). Uses TanStack `Link` with `activeProps` for active styling. Self-contained dark panel.

- [ ] **Step 1: Write failing render test**

Create `frontend/src/features/shell/__tests__/GovSidebar.test.tsx`:

```tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  createRootRoute,
  createRouter,
  createMemoryHistory,
  RouterProvider,
  Outlet,
} from '@tanstack/react-router'
import { GovSidebar } from '../components/GovSidebar'

function renderInRouter() {
  const rootRoute = createRootRoute({
    component: () => (
      <>
        <GovSidebar />
        <Outlet />
      </>
    ),
  })
  const router = createRouter({
    routeTree: rootRoute,
    history: createMemoryHistory({ initialEntries: ['/dashboard'] }),
  })
  render(<RouterProvider router={router as never} />)
}

describe('GovSidebar', () => {
  it('renders the brand and all nav labels', async () => {
    renderInRouter()
    expect(await screen.findByText('AI4SIDS-Gov')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('shows the alerts badge', async () => {
    renderInRouter()
    expect(await screen.findByText('6')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `pnpm test src/features/shell/__tests__/GovSidebar.test.tsx`
Expected: FAIL ("Cannot find module '../components/GovSidebar'").

- [ ] **Step 3: Implement `GovSidebar.tsx`**

Create `frontend/src/features/shell/components/GovSidebar.tsx`:

```tsx
import { Link } from '@tanstack/react-router'
import { Waves } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { NAV_ITEMS } from '@/features/shell/nav'
import { ThemeToggle } from '@/features/shell/components/ThemeToggle'

export function GovSidebar() {
  return (
    <aside className="flex h-full w-64 flex-col bg-slate-900 text-slate-100">
      {/* Brand */}
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
          <Waves className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="text-base font-bold leading-tight">AI4SIDS-Gov</div>
          <div className="text-[11px] leading-tight text-slate-400">
            Climate Resilience &amp; Preparedness Platform
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-2">
        {NAV_ITEMS.map(({ label, to, icon: Icon, badge }) => (
          <Link
            key={to}
            to={to}
            activeOptions={{ exact: to === '/dashboard' }}
            activeProps={{ className: 'bg-blue-600 text-white hover:bg-blue-600' }}
            inactiveProps={{ className: 'text-slate-300 hover:bg-white/10 hover:text-white' }}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span className="flex-1">{label}</span>
            {badge ? (
              <Badge className="bg-red-500 px-1.5 text-[11px] text-white hover:bg-red-500">
                {badge}
              </Badge>
            ) : null}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/10 px-3 py-3">
        <ThemeToggle />
        <div className="px-3 pt-2 text-[11px] text-slate-500">v1.0.0</div>
      </div>
    </aside>
  )
}

export default GovSidebar
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pnpm test src/features/shell/__tests__/GovSidebar.test.tsx`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/shell/components/GovSidebar.tsx frontend/src/features/shell/__tests__/GovSidebar.test.tsx
git commit -m "feat(shell): add GovSidebar

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: GovTopBar

**Files:**
- Create: `frontend/src/features/shell/components/GovTopBar.tsx`

**Interfaces:**
- Consumes: `getNavItemByPath` (Task 3), `GovSidebar` (Task 4), shadcn `Sheet`, `useAuth` from `@/lib/auth/AuthContext`, `useRouterState`/`useNavigate` from `@tanstack/react-router`.
- Produces: named export `GovTopBar` (no props). Resolves the page title from the current path; renders a mobile hamburger that opens the sidebar in a `Sheet`, the bell, country `Select`, and a user `DropdownMenu` with Logout.

- [ ] **Step 1: Implement `GovTopBar.tsx`**

Create `frontend/src/features/shell/components/GovTopBar.tsx`:

```tsx
import { useNavigate, useRouterState } from '@tanstack/react-router'
import { Bell, ChevronDown, LogOut, Menu, UserRound } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { getNavItemByPath } from '@/features/shell/nav'
import { GovSidebar } from '@/features/shell/components/GovSidebar'
import { useAuth } from '@/lib/auth/AuthContext'

export function GovTopBar() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const title = getNavItemByPath(pathname)?.label ?? 'Dashboard'

  const handleLogout = () => {
    logout()
    navigate({ to: '/' })
  }

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-6">
      <div className="flex items-center gap-3">
        {/* Mobile nav drawer */}
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open navigation">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 border-0 p-0">
            <SheetTitle className="sr-only">Navigation</SheetTitle>
            <GovSidebar />
          </SheetContent>
        </Sheet>
        <h1 className="text-lg font-semibold">{title}</h1>
      </div>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" aria-label="Notifications" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500" />
        </Button>

        <Select defaultValue="tt">
          <SelectTrigger className="w-[170px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="tt">Trinidad &amp; Tobago</SelectItem>
          </SelectContent>
        </Select>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-700">
                <UserRound className="h-4 w-4" />
              </span>
              <span className="text-sm font-medium">MPAAI Admin</span>
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}

export default GovTopBar
```

- [ ] **Step 2: Typecheck**

Run: `pnpm exec tsc --noEmit`
Expected: no errors. (If `useAuth` does not export `logout`, open `@/lib/auth/AuthContext` and use the actual logout function name — confirm before adjusting.)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/shell/components/GovTopBar.tsx
git commit -m "feat(shell): add GovTopBar with logout and title resolution

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: GovLayout + placeholder page + wire all routes

**Files:**
- Create: `frontend/src/features/shell/components/GovLayout.tsx`
- Create: `frontend/src/features/placeholder/ComingSoonPage.tsx`
- Modify: `frontend/src/routes/dashboard/route.tsx`
- Modify: `frontend/src/routes/dashboard/index.tsx`
- Create: `frontend/src/routes/dashboard/monitoring.tsx`, `risk.tsx`, `alerts.tsx`, `assistant.tsx`, `resources.tsx`, `reports.tsx`, `data.tsx`, `settings.tsx`
- Test: `frontend/src/features/placeholder/__tests__/ComingSoonPage.test.tsx`

**Interfaces:**
- Consumes: `GovSidebar` (Task 4), `GovTopBar` (Task 5).
- Produces: `GovLayout` (renders sidebar + topbar + `<Outlet/>`); `ComingSoonPage({ title }: { title: string })`. Establishes that every page route renders inside `GovLayout`.

- [ ] **Step 1: Write failing test for ComingSoonPage**

Create `frontend/src/features/placeholder/__tests__/ComingSoonPage.test.tsx`:

```tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ComingSoonPage } from '../ComingSoonPage'

describe('ComingSoonPage', () => {
  it('shows the title and a coming-soon note', () => {
    render(<ComingSoonPage title="Settings" />)
    expect(screen.getByText('Settings')).toBeInTheDocument()
    expect(screen.getByText(/coming soon/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `pnpm test src/features/placeholder/__tests__/ComingSoonPage.test.tsx`
Expected: FAIL ("Cannot find module '../ComingSoonPage'").

- [ ] **Step 3: Implement `ComingSoonPage.tsx`**

Create `frontend/src/features/placeholder/ComingSoonPage.tsx`:

```tsx
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
```

- [ ] **Step 4: Run test to verify pass**

Run: `pnpm test src/features/placeholder/__tests__/ComingSoonPage.test.tsx`
Expected: PASS (1 test).

- [ ] **Step 5: Implement `GovLayout.tsx`**

Create `frontend/src/features/shell/components/GovLayout.tsx`:

```tsx
import { Outlet } from '@tanstack/react-router'
import { GovSidebar } from '@/features/shell/components/GovSidebar'
import { GovTopBar } from '@/features/shell/components/GovTopBar'

export function GovLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop sidebar; mobile uses the Sheet drawer in GovTopBar */}
      <div className="hidden md:block">
        <GovSidebar />
      </div>
      <div className="flex flex-1 flex-col overflow-hidden">
        <GovTopBar />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default GovLayout
```

- [ ] **Step 6: Rewrite `routes/dashboard/route.tsx` to use GovLayout (keep auth guard)**

Replace the entire contents of `frontend/src/routes/dashboard/route.tsx` with:

```tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { GovLayout } from '@/features/shell/components/GovLayout'

export const Route = createFileRoute('/dashboard')({
  beforeLoad: () => {
    const token = localStorage.getItem('ai4sids_token')
    if (!token) {
      throw redirect({ to: '/' })
    }
  },
  component: GovLayout,
})
```

- [ ] **Step 7: Replace `routes/dashboard/index.tsx` with a thin placeholder mount (temporary)**

Replace the entire contents of `frontend/src/routes/dashboard/index.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/')({
  component: () => <ComingSoonPage title="Dashboard" />,
})
```

(Task 8 replaces this with the real `DashboardPage`.)

- [ ] **Step 8: Create the seven new route files**

Each of these is a thin wrapper. Create them now pointing at `ComingSoonPage` so the shell is fully navigable; later tasks swap the real pages in.

`frontend/src/routes/dashboard/monitoring.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/monitoring')({
  component: () => <ComingSoonPage title="Real-time Monitoring" />,
})
```

`frontend/src/routes/dashboard/risk.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/risk')({
  component: () => <ComingSoonPage title="Risk & Vulnerability" />,
})
```

`frontend/src/routes/dashboard/alerts.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/alerts')({
  component: () => <ComingSoonPage title="Alerts & Notifications" />,
})
```

`frontend/src/routes/dashboard/assistant.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/assistant')({
  component: () => <ComingSoonPage title="AI Preparedness Assistant" />,
})
```

`frontend/src/routes/dashboard/resources.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/resources')({
  component: () => <ComingSoonPage title="Resources & Guidance" />,
})
```

`frontend/src/routes/dashboard/reports.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/reports')({
  component: () => <ComingSoonPage title="Reports & Analytics" />,
})
```

`frontend/src/routes/dashboard/data.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/data')({
  component: () => <ComingSoonPage title="Data Management" />,
})
```

`frontend/src/routes/dashboard/settings.tsx`:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ComingSoonPage } from '@/features/placeholder/ComingSoonPage'

export const Route = createFileRoute('/dashboard/settings')({
  component: () => <ComingSoonPage title="Settings" />,
})
```

- [ ] **Step 9: Start the dev server so the router plugin regenerates the route tree, then typecheck**

Run: `pnpm dev` (let it boot, confirm no compile errors in output, then stop it). Then:
Run: `pnpm exec tsc --noEmit`
Expected: no errors; `src/routeTree.gen.ts` now includes the new routes.

- [ ] **Step 10: Manual verification**

With `pnpm dev` running, log in (or set `localStorage.ai4sids_token`), visit `http://localhost:3004/dashboard`. Confirm: dark sidebar with all 9 items, active highlight follows navigation, alerts badge shows `6`, top bar title changes per page, theme toggle flips light/dark and persists across reload, logout returns to `/`.

- [ ] **Step 11: Run full test suite**

Run: `pnpm test`
Expected: all tests PASS.

- [ ] **Step 12: Commit**

```bash
git add frontend/src/features/shell/components/GovLayout.tsx frontend/src/features/placeholder frontend/src/routes/dashboard
git commit -m "feat(shell): add GovLayout and wire all dashboard routes

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 7: Alerts feature (owns shared AlertCard)

**Files:**
- Create: `frontend/src/features/alerts/data.ts`
- Create: `frontend/src/features/alerts/filter.ts`
- Create: `frontend/src/features/alerts/components/AlertCard.tsx`
- Create: `frontend/src/features/alerts/AlertsPage.tsx`
- Modify: `frontend/src/routes/dashboard/alerts.tsx`
- Test: `frontend/src/features/alerts/__tests__/filter.test.ts`
- Test: `frontend/src/features/alerts/__tests__/AlertCard.test.tsx`

**Interfaces:**
- Consumes: `AlertItem`, `AlertSeverity` (Task 3).
- Produces:
  - `ALERTS: AlertItem[]` (6 items: 2 `warning`, 1 `alert`, 3 `advisory`... see counts below).
  - `type AlertFilter = 'all' | 'alert' | 'warning'`; `filterAlerts(alerts: AlertItem[], filter: AlertFilter): AlertItem[]`.
  - `AlertCard({ alert }: { alert: AlertItem })` — exported for reuse by the dashboard.

**Seed counts** (mock shows All 6 / Alerts 3 / Warnings 2): use severities so `warning` count = 2 and `alert` count = 3 (remaining 1 is `advisory`). "Warnings" chip filters `severity === 'warning'`; "Alerts" chip filters `severity === 'alert'`.

- [ ] **Step 1: Write failing test for the filter**

Create `frontend/src/features/alerts/__tests__/filter.test.ts`:

```ts
import { describe, it, expect } from 'vitest'
import { filterAlerts } from '../filter'
import { ALERTS } from '../data'

describe('filterAlerts', () => {
  it('returns all 6 for "all"', () => {
    expect(filterAlerts(ALERTS, 'all')).toHaveLength(6)
  })
  it('returns 2 warnings', () => {
    expect(filterAlerts(ALERTS, 'warning')).toHaveLength(2)
  })
  it('returns 3 alerts', () => {
    expect(filterAlerts(ALERTS, 'alert')).toHaveLength(3)
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `pnpm test src/features/alerts/__tests__/filter.test.ts`
Expected: FAIL (modules not found).

- [ ] **Step 3: Implement `data.ts`**

Create `frontend/src/features/alerts/data.ts`:

```ts
import type { AlertItem } from '@/features/shell/types'

export const ALERTS: AlertItem[] = [
  {
    id: 'a1',
    title: 'Heavy Rainfall Warning',
    location: 'Eastern Trinidad',
    timestamp: 'May 21, 2025 8:30 AM',
    severity: 'warning',
  },
  {
    id: 'a2',
    title: 'Flood Watch',
    location: 'Caroni Basin',
    timestamp: 'May 21, 2025 7:45 AM',
    severity: 'alert',
  },
  {
    id: 'a3',
    title: 'Small Craft Advisory',
    location: 'Coastal Waters',
    timestamp: 'May 21, 2025 7:48 AM',
    severity: 'advisory',
  },
  {
    id: 'a4',
    title: 'High Tide Advisory',
    location: 'Port of Spain',
    timestamp: 'May 21, 2025 6:30 AM',
    severity: 'alert',
  },
  {
    id: 'a5',
    title: 'Landslide Warning',
    location: 'Northern Range',
    timestamp: 'May 21, 2025 6:10 AM',
    severity: 'warning',
  },
  {
    id: 'a6',
    title: 'River Level Alert',
    location: 'Sangre Grande',
    timestamp: 'May 21, 2025 5:55 AM',
    severity: 'alert',
  },
]
```

- [ ] **Step 4: Implement `filter.ts`**

Create `frontend/src/features/alerts/filter.ts`:

```ts
import type { AlertItem } from '@/features/shell/types'

export type AlertFilter = 'all' | 'alert' | 'warning'

export function filterAlerts(
  alerts: AlertItem[],
  filter: AlertFilter,
): AlertItem[] {
  if (filter === 'all') return alerts
  return alerts.filter((a) => a.severity === filter)
}
```

- [ ] **Step 5: Run tests to verify pass**

Run: `pnpm test src/features/alerts/__tests__/filter.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 6: Write failing test for AlertCard**

Create `frontend/src/features/alerts/__tests__/AlertCard.test.tsx`:

```tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AlertCard } from '../components/AlertCard'

describe('AlertCard', () => {
  it('renders title, location and timestamp', () => {
    render(
      <AlertCard
        alert={{
          id: 'a1',
          title: 'Heavy Rainfall Warning',
          location: 'Eastern Trinidad',
          timestamp: 'May 21, 2025 8:30 AM',
          severity: 'warning',
        }}
      />,
    )
    expect(screen.getByText('Heavy Rainfall Warning')).toBeInTheDocument()
    expect(screen.getByText('Eastern Trinidad')).toBeInTheDocument()
    expect(screen.getByText('May 21, 2025 8:30 AM')).toBeInTheDocument()
  })
})
```

- [ ] **Step 7: Run to verify failure**

Run: `pnpm test src/features/alerts/__tests__/AlertCard.test.tsx`
Expected: FAIL ("Cannot find module '../components/AlertCard'").

- [ ] **Step 8: Implement `AlertCard.tsx`**

Create `frontend/src/features/alerts/components/AlertCard.tsx`:

```tsx
import { AlertTriangle, Bell, Info, MapPin, Clock } from 'lucide-react'
import type { AlertItem, AlertSeverity } from '@/features/shell/types'

const SEVERITY_STYLES: Record<
  AlertSeverity,
  { border: string; bg: string; icon: typeof Bell; iconColor: string }
> = {
  warning: { border: 'border-l-red-500', bg: 'bg-red-50', icon: AlertTriangle, iconColor: 'text-red-500' },
  alert: { border: 'border-l-amber-500', bg: 'bg-amber-50', icon: Bell, iconColor: 'text-amber-500' },
  advisory: { border: 'border-l-blue-500', bg: 'bg-blue-50', icon: Info, iconColor: 'text-blue-500' },
}

export function AlertCard({ alert }: { alert: AlertItem }) {
  const style = SEVERITY_STYLES[alert.severity]
  const Icon = style.icon
  return (
    <div className={`flex gap-3 rounded-lg border border-l-4 ${style.border} ${style.bg} p-3`}>
      <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${style.iconColor}`} />
      <div className="min-w-0 flex-1">
        <div className="font-medium text-slate-900">{alert.title}</div>
        <div className="mt-1 flex items-center gap-1 text-xs text-slate-600">
          <MapPin className="h-3 w-3" />
          {alert.location}
        </div>
        <div className="mt-0.5 flex items-center gap-1 text-xs text-slate-500">
          <Clock className="h-3 w-3" />
          {alert.timestamp}
        </div>
      </div>
    </div>
  )
}

export default AlertCard
```

- [ ] **Step 9: Run test to verify pass**

Run: `pnpm test src/features/alerts/__tests__/AlertCard.test.tsx`
Expected: PASS (1 test).

- [ ] **Step 10: Implement `AlertsPage.tsx`**

Create `frontend/src/features/alerts/AlertsPage.tsx`:

```tsx
import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ALERTS } from '@/features/alerts/data'
import { filterAlerts, type AlertFilter } from '@/features/alerts/filter'
import { AlertCard } from '@/features/alerts/components/AlertCard'

const FILTERS: { key: AlertFilter; label: string; count: number }[] = [
  { key: 'all', label: 'All', count: ALERTS.length },
  { key: 'alert', label: 'Alerts', count: filterAlerts(ALERTS, 'alert').length },
  { key: 'warning', label: 'Warnings', count: filterAlerts(ALERTS, 'warning').length },
]

export function AlertsPage() {
  const [filter, setFilter] = useState<AlertFilter>('all')
  const visible = filterAlerts(ALERTS, filter)

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>Alerts &amp; Notifications</CardTitle>
          <p className="text-sm text-muted-foreground">Active and recent alerts</p>
          <div className="flex gap-2 pt-2">
            {FILTERS.map((f) => (
              <Button
                key={f.key}
                size="sm"
                variant={filter === f.key ? 'default' : 'outline'}
                onClick={() => setFilter(f.key)}
              >
                {f.label} ({f.count})
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {visible.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export default AlertsPage
```

- [ ] **Step 11: Point the route at the real page**

Replace the entire contents of `frontend/src/routes/dashboard/alerts.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { AlertsPage } from '@/features/alerts/AlertsPage'

export const Route = createFileRoute('/dashboard/alerts')({
  component: AlertsPage,
})
```

- [ ] **Step 12: Typecheck, test, and manual check**

Run: `pnpm exec tsc --noEmit` → no errors.
Run: `pnpm test` → all PASS.
With `pnpm dev`: visit `/dashboard/alerts`, confirm 6 cards, chips filter to 3 (Alerts) and 2 (Warnings).

- [ ] **Step 13: Commit**

```bash
git add frontend/src/features/alerts frontend/src/routes/dashboard/alerts.tsx
git commit -m "feat(alerts): add alerts page with shared AlertCard

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 8: Dashboard feature + reusable BaseMap

**Files:**
- Create: `frontend/src/features/shell/components/BaseMap.tsx`
- Create: `frontend/src/features/dashboard/data.ts`
- Create: `frontend/src/features/dashboard/components/StatCard.tsx`
- Create: `frontend/src/features/dashboard/components/WeatherOverviewCard.tsx`
- Create: `frontend/src/features/dashboard/DashboardPage.tsx`
- Modify: `frontend/src/routes/dashboard/index.tsx`

**Interfaces:**
- Consumes: `AlertCard` + `ALERTS` (Task 7).
- Produces:
  - `interface MapMarker { id: string; label: string; lat: number; lng: number; color: string; value?: string }`
  - `BaseMap({ markers, height, center, zoom }: { markers: MapMarker[]; height?: string; center?: [number, number]; zoom?: number })` — reusable Leaflet map (used by dashboard, monitoring, risk). Default center `[10.5, -61.3]`, zoom `9`, height `h-96`.
  - `StatCard`, `WeatherOverviewCard`, `DashboardPage`.

- [ ] **Step 1: Implement reusable `BaseMap.tsx`**

Create `frontend/src/features/shell/components/BaseMap.tsx`:

```tsx
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

export interface MapMarker {
  id: string
  label: string
  lat: number
  lng: number
  color: string
  value?: string
}

interface BaseMapProps {
  markers: MapMarker[]
  height?: string
  center?: [number, number]
  zoom?: number
}

export function BaseMap({
  markers,
  height = 'h-96',
  center = [10.5, -61.3],
  zoom = 9,
}: BaseMapProps) {
  return (
    <div className={`w-full ${height} overflow-hidden rounded-lg border`}>
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%', zIndex: 1 }}>
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
          attribution='© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        {markers.map((m) => (
          <CircleMarker
            key={m.id}
            center={[m.lat, m.lng]}
            radius={11}
            pathOptions={{ color: m.color, fillColor: m.color, fillOpacity: 0.75, weight: 2 }}
          >
            <Tooltip>
              <span className="font-medium">{m.label}</span>
              {m.value ? <span> — {m.value}</span> : null}
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}

export default BaseMap
```

- [ ] **Step 2: Implement dashboard `data.ts`**

Create `frontend/src/features/dashboard/data.ts`:

```ts
import type { MapMarker } from '@/features/shell/components/BaseMap'

export interface Stat {
  id: string
  label: string
  value: string
  hint?: string
}

export const STATS: Stat[] = [
  { id: 'risk', label: 'Risk Level', value: 'Moderate', hint: 'as of yesterday' },
  { id: 'alerts', label: 'Active Alerts', value: '2', hint: 'View alerts' },
  { id: 'areas', label: 'Affected Areas', value: '5', hint: 'communities' },
  { id: 'pop', label: 'Population at Risk', value: '24,560' },
  { id: 'shelters', label: 'Shelters Ready', value: '18', hint: 'View shelters' },
]

export const RISK_MARKERS: MapMarker[] = [
  { id: 'pos', label: 'Port of Spain', lat: 10.66, lng: -61.51, color: '#f59e0b', value: 'Moderate' },
  { id: 'arima', label: 'Arima', lat: 10.64, lng: -61.28, color: '#ef4444', value: 'High' },
  { id: 'sando', label: 'San Fernando', lat: 10.28, lng: -61.47, color: '#22c55e', value: 'Low' },
  { id: 'sangre', label: 'Sangre Grande', lat: 10.59, lng: -61.13, color: '#f59e0b', value: 'Moderate' },
  { id: 'tobago', label: 'Tobago', lat: 11.18, lng: -60.74, color: '#22c55e', value: 'Low' },
]

export interface WeatherSummary {
  place: string
  temperatureC: number
  condition: string
  windKmh: number
  humidityPct: number
  rainfallMm: number
}

export const WEATHER: WeatherSummary = {
  place: 'Port of Spain',
  temperatureC: 29,
  condition: 'Partly Cloudy',
  windKmh: 18,
  humidityPct: 78,
  rainfallMm: 12.4,
}

export interface UpcomingEvent {
  id: string
  title: string
  date: string
  tag: string
}

export const UPCOMING_EVENTS: UpcomingEvent[] = [
  { id: 'e1', title: 'Heavy Rainfall Watch', date: 'May 21, 2025', tag: 'Watch' },
  { id: 'e2', title: 'High Tide Advisory', date: 'May 22, 2025', tag: 'Advisory' },
]
```

- [ ] **Step 3: Implement `StatCard.tsx`**

Create `frontend/src/features/dashboard/components/StatCard.tsx`:

```tsx
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
```

- [ ] **Step 4: Implement `WeatherOverviewCard.tsx`**

Create `frontend/src/features/dashboard/components/WeatherOverviewCard.tsx`:

```tsx
import { Cloud, Droplets, Wind } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { WEATHER, UPCOMING_EVENTS } from '@/features/dashboard/data'

export function WeatherOverviewCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Weather Overview</CardTitle>
        <p className="text-xs text-muted-foreground">{WEATHER.place}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-4xl font-bold">{WEATHER.temperatureC}°C</div>
            <div className="text-sm text-muted-foreground">{WEATHER.condition}</div>
          </div>
          <Cloud className="h-12 w-12 text-amber-400" />
        </div>
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div className="flex items-center gap-1">
            <Droplets className="h-4 w-4 text-blue-500" />
            {WEATHER.rainfallMm} mm
          </div>
          <div className="flex items-center gap-1">
            <Wind className="h-4 w-4 text-slate-500" />
            {WEATHER.windKmh} km/h
          </div>
          <div className="flex items-center gap-1">
            <Droplets className="h-4 w-4 text-cyan-500" />
            {WEATHER.humidityPct}%
          </div>
        </div>
        <div>
          <div className="mb-2 text-sm font-semibold">Upcoming Events</div>
          <div className="space-y-2">
            {UPCOMING_EVENTS.map((e) => (
              <div key={e.id} className="flex items-center justify-between rounded-md border p-2">
                <div>
                  <div className="text-sm font-medium">{e.title}</div>
                  <div className="text-xs text-muted-foreground">{e.date}</div>
                </div>
                <Badge variant="outline">{e.tag}</Badge>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default WeatherOverviewCard
```

- [ ] **Step 5: Implement `DashboardPage.tsx`**

Create `frontend/src/features/dashboard/DashboardPage.tsx`:

```tsx
import { Download, Settings2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BaseMap } from '@/features/shell/components/BaseMap'
import { StatCard } from '@/features/dashboard/components/StatCard'
import { WeatherOverviewCard } from '@/features/dashboard/components/WeatherOverviewCard'
import { STATS, RISK_MARKERS } from '@/features/dashboard/data'
import { AlertCard } from '@/features/alerts/components/AlertCard'
import { ALERTS } from '@/features/alerts/data'

export function DashboardPage() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">National Overview</h2>
          <p className="text-sm text-muted-foreground">Trinidad &amp; Tobago</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
          <Button variant="outline" size="sm">
            <Settings2 className="mr-2 h-4 w-4" />
            Customise
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        {STATS.map((s) => (
          <StatCard key={s.id} stat={s} />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Risk Map</CardTitle>
          </CardHeader>
          <CardContent>
            <BaseMap markers={RISK_MARKERS} />
          </CardContent>
        </Card>
        <WeatherOverviewCard />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Alerts &amp; Notifications</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          {ALERTS.slice(0, 3).map((a) => (
            <AlertCard key={a.id} alert={a} />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export default DashboardPage
```

- [ ] **Step 6: Point the index route at DashboardPage**

Replace the entire contents of `frontend/src/routes/dashboard/index.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { DashboardPage } from '@/features/dashboard/DashboardPage'

export const Route = createFileRoute('/dashboard/')({
  component: DashboardPage,
})
```

- [ ] **Step 7: Typecheck, test, manual check**

Run: `pnpm exec tsc --noEmit` → no errors.
Run: `pnpm test` → all PASS.
With `pnpm dev`: visit `/dashboard`, confirm 5 stat cards, a rendered Leaflet map with markers, weather card, and 3 alert cards.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/features/shell/components/BaseMap.tsx frontend/src/features/dashboard frontend/src/routes/dashboard/index.tsx
git commit -m "feat(dashboard): add national overview page and reusable BaseMap

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 9: Monitoring feature

**Files:**
- Create: `frontend/src/features/monitoring/data.ts`
- Create: `frontend/src/features/monitoring/MonitoringPage.tsx`
- Modify: `frontend/src/routes/dashboard/monitoring.tsx`
- Setup: install shadcn `tabs`.

**Interfaces:**
- Consumes: `BaseMap`, `MapMarker` (Task 8); shadcn `Tabs`.
- Produces: `MonitoringPage`. Tabs: Rainfall / River Levels / Weather Stations / Tide Levels (only Rainfall is populated; the other three show a short "No additional data in this demo" note).

- [ ] **Step 1: Install the shadcn Tabs component**

Run: `pnpm dlx shadcn@latest add tabs --yes`
Expected: creates `frontend/src/components/ui/tabs.tsx`.

- [ ] **Step 2: Implement `data.ts`**

Create `frontend/src/features/monitoring/data.ts`:

```ts
import type { MapMarker } from '@/features/shell/components/BaseMap'

export interface RainfallStation {
  id: string
  name: string
  mm: number
  lat: number
  lng: number
}

export const RAINFALL_STATIONS: RainfallStation[] = [
  { id: 'arima', name: 'Arima', mm: 23.6, lat: 10.64, lng: -61.28 },
  { id: 'sangre', name: 'Sangre Grande', mm: 16.3, lat: 10.59, lng: -61.13 },
  { id: 'tunapuna', name: 'Tunapuna', mm: 12.8, lat: 10.65, lng: -61.39 },
  { id: 'sando', name: 'San Fernando', mm: 8.4, lat: 10.28, lng: -61.47 },
  { id: 'pos', name: 'Port of Spain', mm: 5.2, lat: 10.66, lng: -61.51 },
  { id: 'mayaro', name: 'Mayaro', mm: 3.8, lat: 10.29, lng: -61.0 },
  { id: 'tobago', name: 'Tobago', mm: 2.1, lat: 11.18, lng: -60.74 },
]

// Green→amber→red by rainfall amount.
export function rainfallColor(mm: number): string {
  if (mm >= 16) return '#ef4444'
  if (mm >= 8) return '#f59e0b'
  return '#22c55e'
}

export const RAINFALL_MARKERS: MapMarker[] = RAINFALL_STATIONS.map((s) => ({
  id: s.id,
  label: s.name,
  lat: s.lat,
  lng: s.lng,
  color: rainfallColor(s.mm),
  value: `${s.mm} mm`,
}))
```

- [ ] **Step 3: Implement `MonitoringPage.tsx`**

Create `frontend/src/features/monitoring/MonitoringPage.tsx`:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BaseMap } from '@/features/shell/components/BaseMap'
import {
  RAINFALL_STATIONS,
  RAINFALL_MARKERS,
  rainfallColor,
} from '@/features/monitoring/data'

const EMPTY_TABS = ['River Levels', 'Weather Stations', 'Tide Levels']

export function MonitoringPage() {
  return (
    <div className="space-y-4 p-6">
      <div>
        <h2 className="text-xl font-bold">Real-time Monitoring</h2>
        <p className="text-sm text-muted-foreground">Live feeds and sensor data</p>
      </div>

      <Tabs defaultValue="rainfall">
        <TabsList>
          <TabsTrigger value="rainfall">Rainfall</TabsTrigger>
          <TabsTrigger value="river">River Levels</TabsTrigger>
          <TabsTrigger value="stations">Weather Stations</TabsTrigger>
          <TabsTrigger value="tide">Tide Levels</TabsTrigger>
        </TabsList>

        <TabsContent value="rainfall">
          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardContent className="pt-6">
                <BaseMap markers={RAINFALL_MARKERS} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Rainfall (mm) — Last 24h</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {RAINFALL_STATIONS.map((s) => (
                  <div key={s.id} className="flex items-center justify-between text-sm">
                    <span>{s.name}</span>
                    <span className="font-semibold" style={{ color: rainfallColor(s.mm) }}>
                      {s.mm} mm
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {EMPTY_TABS.map((label, i) => (
          <TabsContent key={label} value={['river', 'stations', 'tide'][i]}>
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                No additional data in this demo.
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      <p className="text-xs text-muted-foreground">
        Data updates every 15 minutes · Next update 10:45 AM
      </p>
    </div>
  )
}

export default MonitoringPage
```

- [ ] **Step 4: Point the route at the page**

Replace the entire contents of `frontend/src/routes/dashboard/monitoring.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { MonitoringPage } from '@/features/monitoring/MonitoringPage'

export const Route = createFileRoute('/dashboard/monitoring')({
  component: MonitoringPage,
})
```

- [ ] **Step 5: Typecheck, test, manual check**

Run: `pnpm exec tsc --noEmit` → no errors.
Run: `pnpm test` → all PASS.
With `pnpm dev`: visit `/dashboard/monitoring`, confirm tabs, map with 7 markers, ranked station list (Arima 23.6 → Tobago 2.1), footer text.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ui/tabs.tsx frontend/src/features/monitoring frontend/src/routes/dashboard/monitoring.tsx frontend/package.json frontend/pnpm-lock.yaml
git commit -m "feat(monitoring): add real-time monitoring page

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 10: Risk & Vulnerability feature

**Files:**
- Create: `frontend/src/features/risk/data.ts`
- Create: `frontend/src/features/risk/components/VulnerabilityDonut.tsx`
- Create: `frontend/src/features/risk/RiskPage.tsx`
- Modify: `frontend/src/routes/dashboard/risk.tsx`

**Interfaces:**
- Consumes: `BaseMap`, `MapMarker` (Task 8); shadcn `Tabs` (installed Task 9); `recharts` (installed).
- Produces: `RiskPage`, `VulnerabilityDonut`. Tabs: Flood Risk / Landslide Risk / Heat Risk (Flood populated; other two show the demo note).

- [ ] **Step 1: Implement `data.ts`**

Create `frontend/src/features/risk/data.ts`:

```ts
import type { MapMarker } from '@/features/shell/components/BaseMap'

export interface VulnerabilitySlice {
  label: string
  value: number
  color: string
}

// Total communities = 82.
export const VULNERABILITY: VulnerabilitySlice[] = [
  { label: 'Very High', value: 14, color: '#dc2626' },
  { label: 'High', value: 26, color: '#f97316' },
  { label: 'Moderate', value: 24, color: '#f59e0b' },
  { label: 'Low', value: 9, color: '#3b82f6' },
  { label: 'Very Low', value: 9, color: '#22c55e' },
]

export const TOTAL_COMMUNITIES = VULNERABILITY.reduce((sum, s) => sum + s.value, 0)

export const FLOOD_RISK_MARKERS: MapMarker[] = [
  { id: 'pos', label: 'Port of Spain', lat: 10.66, lng: -61.51, color: '#f59e0b', value: 'Moderate' },
  { id: 'arima', label: 'Arima', lat: 10.64, lng: -61.28, color: '#dc2626', value: 'Very High' },
  { id: 'caroni', label: 'Caroni Basin', lat: 10.5, lng: -61.4, color: '#f97316', value: 'High' },
  { id: 'sando', label: 'San Fernando', lat: 10.28, lng: -61.47, color: '#3b82f6', value: 'Low' },
  { id: 'tobago', label: 'Tobago', lat: 11.18, lng: -60.74, color: '#22c55e', value: 'Very Low' },
]
```

- [ ] **Step 2: Implement `VulnerabilityDonut.tsx`**

Create `frontend/src/features/risk/components/VulnerabilityDonut.tsx`:

```tsx
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { VULNERABILITY, TOTAL_COMMUNITIES } from '@/features/risk/data'

export function VulnerabilityDonut() {
  return (
    <div className="flex items-center gap-6">
      <div className="relative h-44 w-44 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={VULNERABILITY}
              dataKey="value"
              nameKey="label"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={2}
            >
              {VULNERABILITY.map((s) => (
                <Cell key={s.label} fill={s.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold">{TOTAL_COMMUNITIES}</span>
          <span className="text-[11px] text-muted-foreground">Communities</span>
        </div>
      </div>
      <div className="space-y-1.5 text-sm">
        {VULNERABILITY.map((s) => (
          <div key={s.label} className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full" style={{ backgroundColor: s.color }} />
            <span className="flex-1">{s.label}</span>
            <span className="font-medium">{s.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default VulnerabilityDonut
```

- [ ] **Step 3: Implement `RiskPage.tsx`**

Create `frontend/src/features/risk/RiskPage.tsx`:

```tsx
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
```

- [ ] **Step 4: Point the route at the page**

Replace the entire contents of `frontend/src/routes/dashboard/risk.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { RiskPage } from '@/features/risk/RiskPage'

export const Route = createFileRoute('/dashboard/risk')({
  component: RiskPage,
})
```

- [ ] **Step 5: Typecheck, test, manual check**

Run: `pnpm exec tsc --noEmit` → no errors.
Run: `pnpm test` → all PASS.
With `pnpm dev`: visit `/dashboard/risk`, confirm flood map, donut centered on `82`, legend counts (14/26/24/9/9).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/risk frontend/src/routes/dashboard/risk.tsx
git commit -m "feat(risk): add risk & vulnerability page with donut

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 11: AI Preparedness Assistant feature

**Files:**
- Create: `frontend/src/features/assistant/data.ts`
- Create: `frontend/src/features/assistant/AssistantPage.tsx`
- Modify: `frontend/src/routes/dashboard/assistant.tsx`

**Interfaces:**
- Consumes: nothing new.
- Produces: `AssistantPage`. Static transcript + suggested-prompt chips + echo-only input + Clear Chat (resets to the seeded transcript).

- [ ] **Step 1: Implement `data.ts`**

Create `frontend/src/features/assistant/data.ts`:

```ts
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  bullets?: string[]
  time: string
}

export const INITIAL_TRANSCRIPT: ChatMessage[] = [
  {
    id: 'm1',
    role: 'user',
    text: 'What should local authorities do if heavy rainfall is forecast for the next 24 hours?',
    time: '10:31 AM',
  },
  {
    id: 'm2',
    role: 'assistant',
    text: 'Based on the current forecast and risk assessment, here are the recommended actions:',
    bullets: [
      'Monitor rainfall and river levels closely',
      'Inspect and clear drainage systems',
      'Ensure shelters are prepared and supplies are stocked',
      'Alert vulnerable communities and review evacuation plans',
      'Coordinate with ODPM and regional corporations',
    ],
    time: '10:31 AM',
  },
]

export const SUGGESTED_PROMPTS: string[] = [
  'Which areas are most at risk right now?',
  'Summarise the latest flood watch',
  'What supplies should shelters stock?',
]
```

- [ ] **Step 2: Implement `AssistantPage.tsx`**

Create `frontend/src/features/assistant/AssistantPage.tsx`:

```tsx
import { useState } from 'react'
import { Bot, Send } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  INITIAL_TRANSCRIPT,
  SUGGESTED_PROMPTS,
  type ChatMessage,
} from '@/features/assistant/data'

export function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_TRANSCRIPT)
  const [draft, setDraft] = useState('')

  const send = (text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return
    setMessages((prev) => [
      ...prev,
      { id: `u-${prev.length}`, role: 'user', text: trimmed, time: 'now' },
    ])
    setDraft('')
  }

  return (
    <div className="p-6">
      <Card className="flex h-[calc(100vh-7rem)] flex-col">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="h-5 w-5 text-blue-600" />
            AI Preparedness Assistant
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={() => setMessages(INITIAL_TRANSCRIPT)}>
            Clear Chat
          </Button>
        </CardHeader>

        <CardContent className="flex flex-1 flex-col gap-4 overflow-y-auto">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`max-w-[80%] rounded-lg p-3 text-sm ${
                m.role === 'user'
                  ? 'ml-auto bg-blue-600 text-white'
                  : 'bg-muted text-foreground'
              }`}
            >
              <div>{m.text}</div>
              {m.bullets ? (
                <ul className="mt-2 list-disc space-y-1 pl-4">
                  {m.bullets.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              ) : null}
              <div className="mt-1 text-[10px] opacity-70">{m.time}</div>
            </div>
          ))}
        </CardContent>

        <div className="border-t p-3">
          <div className="mb-2 flex flex-wrap gap-2">
            {SUGGESTED_PROMPTS.map((p) => (
              <button
                key={p}
                onClick={() => send(p)}
                className="rounded-full border px-3 py-1 text-xs hover:bg-muted"
              >
                {p}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="Ask a question…"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send(draft)}
            />
            <Button onClick={() => send(draft)} disabled={!draft.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AssistantPage
```

- [ ] **Step 3: Point the route at the page**

Replace the entire contents of `frontend/src/routes/dashboard/assistant.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { AssistantPage } from '@/features/assistant/AssistantPage'

export const Route = createFileRoute('/dashboard/assistant')({
  component: AssistantPage,
})
```

- [ ] **Step 4: Typecheck, test, manual check**

Run: `pnpm exec tsc --noEmit` → no errors.
Run: `pnpm test` → all PASS.
With `pnpm dev`: visit `/dashboard/assistant`, confirm seeded transcript with bullet list, suggested chips append a user bubble, Clear Chat resets.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/assistant frontend/src/routes/dashboard/assistant.tsx
git commit -m "feat(assistant): add static AI preparedness assistant page

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 12: Resources & Guidance feature

**Files:**
- Create: `frontend/src/features/resources/data.ts`
- Create: `frontend/src/features/resources/ResourcesPage.tsx`
- Modify: `frontend/src/routes/dashboard/resources.tsx`

**Interfaces:**
- Consumes: nothing new.
- Produces: `ResourcesPage`. Three sections: Key Preparedness Resources, Quick Reports, Data Partners.

- [ ] **Step 1: Implement `data.ts`**

Create `frontend/src/features/resources/data.ts`:

```ts
import {
  Home,
  Route as RouteIcon,
  Phone,
  Megaphone,
  FileText,
  CalendarDays,
  FileCog,
  type LucideIcon,
} from 'lucide-react'

export interface ResourceLink {
  id: string
  label: string
  hint: string
  icon: LucideIcon
}

export const PREPAREDNESS_RESOURCES: ResourceLink[] = [
  { id: 'shelter', label: 'Shelter Directory', hint: 'View locations', icon: Home },
  { id: 'routes', label: 'Evacuation Routes', hint: 'View map', icon: RouteIcon },
  { id: 'contacts', label: 'Emergency Contacts', hint: 'View directory', icon: Phone },
  { id: 'awareness', label: 'Public Awareness', hint: 'View materials', icon: Megaphone },
]

export const QUICK_REPORTS: ResourceLink[] = [
  { id: 'daily', label: 'Daily Situation Report', hint: 'Generate', icon: FileText },
  { id: 'weekly', label: 'Weekly Report', hint: 'Generate', icon: CalendarDays },
  { id: 'custom', label: 'Custom Report', hint: 'Configure', icon: FileCog },
]

export const DATA_PARTNERS: string[] = [
  'TTMS',
  'ODPM',
  'MPAAI',
  'Ministry of Health',
  'CSO',
  'Regional Corporations',
]
```

- [ ] **Step 2: Implement `ResourcesPage.tsx`**

Create `frontend/src/features/resources/ResourcesPage.tsx`:

```tsx
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
```

- [ ] **Step 3: Point the route at the page**

Replace the entire contents of `frontend/src/routes/dashboard/resources.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ResourcesPage } from '@/features/resources/ResourcesPage'

export const Route = createFileRoute('/dashboard/resources')({
  component: ResourcesPage,
})
```

- [ ] **Step 4: Typecheck, test, manual check**

Run: `pnpm exec tsc --noEmit` → no errors.
Run: `pnpm test` → all PASS.
With `pnpm dev`: visit `/dashboard/resources`, confirm three sections and six partner tiles.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/resources frontend/src/routes/dashboard/resources.tsx
git commit -m "feat(resources): add resources & guidance page

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 13: Reports & Analytics feature

**Files:**
- Create: `frontend/src/features/reports/data.ts`
- Create: `frontend/src/features/reports/ReportsPage.tsx`
- Modify: `frontend/src/routes/dashboard/reports.tsx`

**Interfaces:**
- Consumes: nothing new.
- Produces: `ReportsPage`. System Status panel (4 services with Operational badges + timestamps) and report-generation cards.

- [ ] **Step 1: Implement `data.ts`**

Create `frontend/src/features/reports/data.ts`:

```ts
export interface SystemService {
  id: string
  label: string
  status: 'Operational'
  detail: string
}

export const SYSTEM_STATUS: SystemService[] = [
  { id: 'daily', label: 'Daily Services', status: 'Operational', detail: 'Last run 8:00 AM' },
  { id: 'sensors', label: 'Last 5 Sensors', status: 'Operational', detail: 'All reporting' },
  { id: 'alerts', label: 'Alerts System', status: 'Operational', detail: 'Live' },
  { id: 'backup', label: 'Last Backup', status: 'Operational', detail: '2:00 AM' },
]

export interface ReportType {
  id: string
  label: string
  description: string
}

export const REPORT_TYPES: ReportType[] = [
  { id: 'daily', label: 'Daily Situation Report', description: 'Snapshot of the last 24 hours.' },
  { id: 'weekly', label: 'Weekly Report', description: 'Trends across the past 7 days.' },
  { id: 'custom', label: 'Custom Report', description: 'Choose range and metrics.' },
]
```

- [ ] **Step 2: Implement `ReportsPage.tsx`**

Create `frontend/src/features/reports/ReportsPage.tsx`:

```tsx
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
```

- [ ] **Step 3: Point the route at the page**

Replace the entire contents of `frontend/src/routes/dashboard/reports.tsx` with:

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ReportsPage } from '@/features/reports/ReportsPage'

export const Route = createFileRoute('/dashboard/reports')({
  component: ReportsPage,
})
```

- [ ] **Step 4: Typecheck, test, manual check**

Run: `pnpm exec tsc --noEmit` → no errors.
Run: `pnpm test` → all PASS.
With `pnpm dev`: visit `/dashboard/reports`, confirm 4 status tiles (Operational) and 3 report cards.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/reports frontend/src/routes/dashboard/reports.tsx
git commit -m "feat(reports): add reports & analytics page

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 14: Final verification

**Files:** none (verification only).

- [ ] **Step 1: Full typecheck**

Run: `pnpm exec tsc --noEmit`
Expected: no errors.

- [ ] **Step 2: Full test suite**

Run: `pnpm test`
Expected: all PASS.

- [ ] **Step 3: Production build**

Run: `pnpm build`
Expected: build succeeds with no errors.

- [ ] **Step 4: Manual walkthrough**

With `pnpm dev`, logged in, visit each route and confirm against the spec's verification checklist:
- `/dashboard` — 5 stats, risk map, weather card, 3 alert cards.
- `/dashboard/monitoring` — tabs, rainfall map (7 markers), ranked list, footer.
- `/dashboard/risk` — flood map, donut centered on 82, legend counts.
- `/dashboard/alerts` — 6 cards; chips filter to 3 / 2.
- `/dashboard/assistant` — transcript + bullets; chips append; Clear Chat resets.
- `/dashboard/resources` — three sections, six partners.
- `/dashboard/reports` — 4 status tiles, 3 report cards.
- `/dashboard/data` and `/dashboard/settings` — coming-soon placeholder.
- Sidebar active highlight follows route; alerts badge `6`; theme toggle flips + persists; logout returns to `/`.

- [ ] **Step 5: Run react-doctor**

Invoke the `react-doctor` skill to catch React issues (effect deps, keys, state) across the new feature code. Fix anything it flags.

- [ ] **Step 6: Final commit (if react-doctor produced fixes)**

```bash
git add -A
git commit -m "fix: address react-doctor findings for AI4SIDS-Gov pages

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
