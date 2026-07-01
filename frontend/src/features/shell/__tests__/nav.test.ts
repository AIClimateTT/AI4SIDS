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
