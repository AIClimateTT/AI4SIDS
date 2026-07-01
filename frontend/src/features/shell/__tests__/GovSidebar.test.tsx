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
