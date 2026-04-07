import { describe, expect, it } from 'vitest'

import { constantRoutes } from '../index'

describe('router config', () => {
  it('registers text formatter and pdf team splitter routes', () => {
    const rootRoute = constantRoutes.find((route) => route.path === '/')

    expect(rootRoute?.redirect).toBe('/text-formatter')
    expect(rootRoute?.children).toHaveLength(2)

    const childPaths = rootRoute?.children?.map((route) => route.path)
    expect(childPaths).toEqual(['text-formatter', 'pdf-team-splitter'])

    expect(rootRoute?.children?.[0]?.name).toBe('TextFormatter')
    expect(rootRoute?.children?.[1]?.name).toBe('PdfTeamSplitter')
    expect(rootRoute?.children?.[1]?.meta?.title).toBe('PDF 行程整理')
  })
})
