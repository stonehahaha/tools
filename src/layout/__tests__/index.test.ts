import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import LayoutView from '../index.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
  useRoute: () => ({
    path: '/text-formatter',
  }),
}))

describe('layout brand icon', () => {
  it('uses the dedicated favicon asset in the top brand block', () => {
    const wrapper = mount(LayoutView, {
      global: {
        plugins: [ElementPlus],
        stubs: {
          RouterView: true,
        },
      },
    })

    const brandImage = wrapper.find('[data-testid="brand-mark"]')
    expect(brandImage.exists()).toBe(true)
    expect(brandImage.attributes('src')).toBe('/favicon-data-processing.svg')
  })
})
