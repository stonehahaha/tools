import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import * as pdfTeamSplitApi from '@/api/pdfTeamSplit'
import PdfTeamSplitterView from '../index.vue'

const makeFileList = (files: File[]) => {
  const fileList: Partial<FileList> & Record<number, File> = {
    length: files.length,
    item(index: number) {
      return files[index] ?? null
    },
    [Symbol.iterator]() {
      let index = 0
      return {
        next: () => {
          const done = index >= files.length
          const value = done ? undefined : files[index]
          index += 1
          return { done, value }
        },
      }
    },
  }

  files.forEach((file, index) => {
    fileList[index] = file
  })

  return fileList as FileList
}

describe('PdfTeamSplitterView', () => {
  it('locks the action button until both files are present', () => {
    const wrapper = mount(PdfTeamSplitterView)
    const primaryButton = wrapper.find('[data-testid="split-button"]')

    expect(primaryButton.attributes('disabled')).toBeDefined()
  })

  it('uploads files and downloads the split result', async () => {
    const blob = new Blob(['team-split'], { type: 'application/pdf' })
    const requestSpy = vi
      .spyOn(pdfTeamSplitApi, 'requestPdfTeamSplit')
      .mockResolvedValue(blob)
    const downloadSpy = vi
      .spyOn(pdfTeamSplitApi, 'downloadPdfTeamSplitResult')
      .mockImplementation(() => undefined)

    const wrapper = mount(PdfTeamSplitterView)
    const rosterInput = wrapper.find('[data-testid="roster-input"]')
    const pdfInput = wrapper.find('[data-testid="pdf-input"]')

    const rosterFile = new File(['roster-data'], 'roster.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const pdfFile = new File(['pdf-data'], 'schedule.pdf', {
      type: 'application/pdf',
    })

    Object.defineProperty(rosterInput.element, 'files', {
      value: makeFileList([rosterFile]),
      writable: false,
    })
    await rosterInput.trigger('change')

    Object.defineProperty(pdfInput.element, 'files', {
      value: makeFileList([pdfFile]),
      writable: false,
    })
    await pdfInput.trigger('change')

    const primaryButton = wrapper.find('[data-testid="split-button"]')
    expect(primaryButton.attributes('disabled')).toBeUndefined()

    await primaryButton.trigger('click')
    await flushPromises()

    expect(requestSpy).toHaveBeenCalledTimes(1)
    const formData = requestSpy.mock.calls[0][0] as FormData
    expect(formData.get('roster')).toBe(rosterFile)
    expect(formData.get('pdf')).toBe(pdfFile)
    expect(formData.get('name_column')).toBe('B')
    expect(formData.get('team_column')).toBe('C')
    expect(formData.get('fuzzy_threshold')).toBe('80')

    expect(downloadSpy).toHaveBeenCalledTimes(1)
    expect(downloadSpy).toHaveBeenCalledWith(blob, 'pdf-team-split-result.zip')
  })
})
