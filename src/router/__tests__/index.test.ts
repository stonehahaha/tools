import { describe, expect, it } from 'vitest'

import { constantRoutes } from '../index'

describe('router config', () => {
  it('keeps only the text formatter tool', () => {
    const rootRoute = constantRoutes.find((route) => route.path === '/')

    expect(rootRoute?.redirect).toBe('/text-formatter')
    expect(rootRoute?.children).toHaveLength(1)
    expect(rootRoute?.children?.[0]?.path).toBe('text-formatter')
    expect(rootRoute?.children?.[0]?.name).toBe('TextFormatter')
    expect(rootRoute?.children?.some((route) => route.path === 'date-formatter')).toBe(false)
  })
})
