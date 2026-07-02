import { describe, expect, it } from 'vitest'
import { LayoutDashboard } from 'lucide-react'
import { filterNavByRole } from '../nav'
import type { NavItem } from '../types'

describe('filterNavByRole', () => {
  const items: NavItem[] = [
    { label: 'Open', to: '/a', icon: LayoutDashboard },
    { label: 'Admins', to: '/b', icon: LayoutDashboard, roles: ['org_admin'] },
    { label: 'Platform', to: '/c', icon: LayoutDashboard, roles: ['super_admin'] },
  ]

  it('unrestricted items are visible to everyone, even logged-out', () => {
    expect(filterNavByRole(items, null).map((i) => i.label)).toEqual(['Open'])
  })

  it('member sees only unrestricted items', () => {
    expect(filterNavByRole(items, 'member').map((i) => i.label)).toEqual(['Open'])
  })

  it('org_admin sees org_admin items but not super_admin items', () => {
    expect(filterNavByRole(items, 'org_admin').map((i) => i.label)).toEqual([
      'Open',
      'Admins',
    ])
  })

  it('super_admin sees everything', () => {
    expect(filterNavByRole(items, 'super_admin').map((i) => i.label)).toEqual([
      'Open',
      'Admins',
      'Platform',
    ])
  })
})
