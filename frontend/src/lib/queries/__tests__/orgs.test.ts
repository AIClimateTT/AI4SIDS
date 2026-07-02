import { describe, expect, it } from 'vitest'
import { orgKeys, orgQueries } from '../orgs'

describe('orgKeys', () => {
  it('builds hierarchical keys', () => {
    expect(orgKeys.all()).toEqual(['orgs'])
    expect(orgKeys.lists()).toEqual(['orgs', 'list'])
    expect(orgKeys.list()).toEqual(['orgs', 'list'])
    expect(orgKeys.users(7)).toEqual(['orgs', 'users', 7])
  })

  it('pairs every key with query options', () => {
    expect(orgQueries.list().queryKey).toEqual(orgKeys.list())
    expect(orgQueries.users(7).queryKey).toEqual(orgKeys.users(7))
    expect(orgQueries.users(0).enabled).toBe(false)
  })
})
