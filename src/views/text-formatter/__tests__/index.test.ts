import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import TextFormatterView from '../index.vue'

vi.mock('element-plus', async () => {
  const actual = await vi.importActual<typeof import('element-plus')>('element-plus')

  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      warning: vi.fn(),
      error: vi.fn(),
    },
  }
})

const passengerSample = `ZHENG/YANQING
成人
ER0775485
380
988.00
CNY
1368
7312180801003
SONG/MEIZHU
成人
ER0775139
380
988.00
CNY
1368
7312180801000`

describe('text formatter view', () => {
  it('renders only the passenger workflow and extracts passenger rows', async () => {
    const wrapper = mount(TextFormatterView, {
      global: {
        plugins: [ElementPlus],
      },
    })

    expect(wrapper.find('.mode-switcher').exists()).toBe(false)
    expect(wrapper.text()).toContain('旅客信息整理')
    expect(wrapper.text()).not.toContain('基础整理')
    expect(wrapper.text()).toContain('加载示例')
    expect(wrapper.text()).toContain('提取旅客信息')

    const textareas = wrapper.findAll('textarea')
    await textareas[0]!.setValue(passengerSample)
    await wrapper.find('button.el-button--primary').trigger('click')
    await flushPromises()

    expect((wrapper.findAll('textarea')[1]!.element as HTMLTextAreaElement).value.trim()).toBe(
      '1\tZHENG/YANQING\t7312180801003\n2\tSONG/MEIZHU\t7312180801000',
    )
  })
})
