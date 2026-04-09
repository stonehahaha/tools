import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

describe('favicon entrypoint', () => {
  it('uses the dedicated data-processing favicon asset', () => {
    const projectRoot = process.cwd()
    const html = readFileSync(resolve(projectRoot, 'index.html'), 'utf8')

    expect(html).toContain('<title>数据处理</title>')
    expect(html).toContain('href="/favicon-data-processing.svg"')
    expect(existsSync(resolve(projectRoot, 'public', 'favicon-data-processing.svg'))).toBe(
      true,
    )
  })
})
