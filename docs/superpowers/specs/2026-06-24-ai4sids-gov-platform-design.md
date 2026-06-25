# AI4SIDS-Gov Platform — Authenticated Area Redesign

**Date:** 2026-06-24
**Status:** Approved design, ready for implementation plan
**Scope:** Frontend only. Static, test-data-driven rebuild of the post-login experience.

## Goal

Replace the current authenticated `/dashboard` area with a multi-page "AI4SIDS-Gov" platform that matches the provided mock (`626E87D3-DF39-4EB3-AB56-0D4FEE6CF3E9.png`). The mock is a cluster of pages shown together for reference — **not** a single scrolling page. Each major page becomes its own route and its own folder under a new `src/features/` directory.

Everything is **fully static with seeded test data** in this pass. No backend wiring (except reuse of the existing `useAuth` for logout and the existing route token guard).

## Decisions (from brainstorming)

- **Page scope:** Build the ~7 pages the mock shows. `Data Management` and `Settings` get nav entries + a simple "coming soon" placeholder page.
- **Old dashboard:** Replaced. Existing components (`sidebar-with-sparklines`, `DataAnalytics`, `location-detail-sheet`, etc.) stay in the repo but are no longer routed. Cleanup is out of scope for this pass.
- **Refactor scope:** New Gov pages only. The public landing page and its components (`Hero`, `RiskMap`, `ForecastPanel`, `login-modal`, `AuthContext`) stay where they are.
- **Maps:** Real Leaflet maps via `react-leaflet` (already installed), centered on Trinidad & Tobago, with static test markers/overlays.
- **Theming:** Working light/dark toggle using Tailwind dark mode + the dark CSS variables already in `styles.css`, persisted to localStorage.
- **AI Assistant:** Fully static — canned transcript, static suggested prompts, echo-only input.
- **Architecture:** Approach A — feature-per-page with thin route files. Shared cross-page widgets live in the feature that owns them and are imported by others (no duplication).

## Architecture

### Folder structure

```
frontend/src/features/
  shell/
    components/
      GovSidebar.tsx        # dark navy nav panel
      GovTopBar.tsx         # page title, bell, country select, user chip
      ThemeToggle.tsx       # light/dark switch (localStorage + <html> class)
      GovLayout.tsx         # composes sidebar + topbar + <Outlet/>
    nav.ts                  # single source of truth for nav items
    theme.ts                # theme get/set/toggle helpers
    types.ts                # shared shell + cross-feature types
  dashboard/
    components/             # StatCard row, RiskMapCard, WeatherOverviewCard, ...
    data.ts                 # seeded test data (typed)
    DashboardPage.tsx
  monitoring/
    components/  data.ts  MonitoringPage.tsx
  risk/
    components/  data.ts  RiskPage.tsx
  alerts/
    components/  data.ts  AlertsPage.tsx     # owns shared AlertCard
  assistant/
    components/  data.ts  AssistantPage.tsx
  resources/
    components/  data.ts  ResourcesPage.tsx
  reports/
    components/  data.ts  ReportsPage.tsx
  placeholder/
    ComingSoonPage.tsx     # reused by data + settings routes
```

### Routing

Under the existing auth-guarded `/dashboard` segment. `routes/dashboard/route.tsx` keeps its `beforeLoad` token check but swaps its layout body for `features/shell/GovLayout`.

| Route | Page |
|---|---|
| `/dashboard/` | Dashboard (National Overview) |
| `/dashboard/monitoring` | Real-time Monitoring |
| `/dashboard/risk` | Risk & Vulnerability |
| `/dashboard/alerts` | Alerts & Notifications |
| `/dashboard/assistant` | AI Preparedness Assistant |
| `/dashboard/resources` | Resources & Guidance |
| `/dashboard/reports` | Reports & Analytics |
| `/dashboard/data` | Coming-soon placeholder |
| `/dashboard/settings` | Coming-soon placeholder |

Each route file is a thin wrapper (~5 lines) that mounts the corresponding feature page. TanStack file-based routing; `routeTree.gen.ts` regenerates.

### Shell

- **GovSidebar** — dark navy panel: AI4SIDS-Gov logo + "Climate Resilience & Preparedness Platform" subtitle; nav items with lucide icons and active-state highlight; alert-count badge (`6`) on Alerts & Notifications; `ThemeToggle` + `v1.0.0` at the bottom. Built from shadcn `Button`/`Badge` + Tailwind as a custom flex column (no shadcn `sidebar` primitive added unless desired later).
- **GovTopBar** — page title (derived from active route via `nav.ts`), notification bell with badge, country `Select` (static, `Trinidad & Tobago`), user chip ("MPAAI Admin") with `DropdownMenu` containing Logout (calls existing `useAuth().logout` + navigate to `/`).
- **ThemeToggle** — toggles `dark` class on `<html>`, persists to localStorage, reads initial value on mount. shadcn components follow via existing CSS variables.
- **Mobile** — desktop is the priority. On small screens the sidebar collapses behind a hamburger in the top bar using shadcn `Sheet`; layout must not break.

## Pages & seeded test data

Each feature folder exports a typed `data.ts`. Numbers below are the seed values.

### dashboard/ — National Overview
- Stat cards: Risk Level `Moderate`, Active Alerts `2`, Affected Areas `5`, Population at Risk `24,560`, Shelters Ready `18`.
- Risk Map (Leaflet, T&T, colored risk markers + legend) beside Weather Overview card (Port of Spain, `29°C`, Partly Cloudy, wind `18 km/h`, humidity `78%`, rainfall `12.4 mm`, Upcoming Events list: Heavy Rainfall Watch, High Tide Advisory).
- Header actions: Export Report, Customise (static buttons).

### monitoring/ — Real-time Monitoring
- shadcn `Tabs`: Rainfall / River Levels / Weather Stations / Tide Levels.
- Leaflet map with color-coded sensor markers beside "Rainfall (mm) — Last 24h" ranked station list: Arima `23.6`, Sangre Grande `16.3`, Tunapuna `12.8`, San Fernando `8.4`, Port of Spain `5.2`, Mayaro `3.8`, Tobago `2.1`. "View all stations →".
- Footer: "Data updates every 15 minutes · Next update 10:45 AM".

### risk/ — Risk & Vulnerability
- shadcn `Tabs`: Flood Risk / Landslide Risk / Heat Risk.
- Flood Risk Index map + legend (Very High/High/Moderate/Low/Very Low) beside Vulnerability Overview donut (recharts) — Total Communities `82`: Very High `14` (17%), High `26` (32%), Moderate `24` (29%), Low `9` (11%), Very Low `9` (11%). "View Detailed Assessment →".

### alerts/ — Alerts & Notifications
- Filter chips: All (`6`) / Alerts (`3`) / Warnings (`2`) — client-side filtering of the static list.
- **AlertCard** (shared, owned here): severity-colored, with icon, title, location, timestamp. Seed items: Heavy Rainfall Warning (Eastern Trinidad), Flood Watch (Caroni Basin), Small Craft Advisory (Coastal Waters), plus enough entries to total 6.

### assistant/ — AI Preparedness Assistant
- Static chat transcript matching the mock (user question about heavy rainfall forecast + assistant bulleted recommendations), suggested-prompt chips, echo-only input field, "Clear Chat" action (clears to initial static state).

### resources/ — Resources & Guidance
- Key Preparedness Resources grid: Shelter Directory, Evacuation Routes, Emergency Contacts, Public Awareness.
- Quick Reports: Daily Situation Report, Weekly Report, Custom Report.
- Data Partners logos/labels: TTMS, ODPM, MPAAI, Ministry of Health, CSO, Regional Corporations.

### reports/ — Reports & Analytics
- System Status panel: Daily Services, Last 5 Sensors, Alerts System, Last Backup — each with an Operational badge and a timestamp.
- Report generation cards (reusing the Quick Reports concept) for a coherent standalone page.

### placeholder/ — data + settings
- Centered "coming soon" card with the page title and a short note.

## Shared types & data flow

- Cross-feature types (nav item, alert, severity, stat) live in `features/shell/types.ts`; page-local types live in their feature.
- Each page imports its own `data.ts`. Swapping to live data later means replacing one import per page with an API hook — no component changes.
- The Dashboard imports `AlertCard` and a slice of alert data from `alerts/` rather than duplicating.

## Out of scope

- Backend/API wiring (data stays static).
- Migrating the public landing page or auth components into `features/`.
- Deleting the old dashboard components.
- Building out `Data Management` and `Settings` beyond placeholders.

## Testing / verification

- App builds and dev server runs without errors.
- Each route renders its page; sidebar nav highlights the active route.
- Theme toggle flips light/dark and persists across reload.
- Leaflet maps render with markers on each map-bearing page.
- Alerts filter chips correctly filter the static list.
- Logout returns to `/` and clears the token.
