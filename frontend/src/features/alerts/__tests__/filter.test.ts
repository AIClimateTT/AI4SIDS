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
