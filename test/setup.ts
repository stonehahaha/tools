import { beforeEach, vi } from 'vitest'

if (typeof window.matchMedia !== 'function') {
  window.matchMedia = (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  })
}

if (!window.navigator.clipboard) {
  Object.defineProperty(window.navigator, 'clipboard', {
    value: {
      writeText: async () => undefined,
    },
    configurable: true,
  })
}

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (typeof window.ResizeObserver === 'undefined') {
  window.ResizeObserver = ResizeObserverStub
}

if (!window.scrollTo) {
  window.scrollTo = () => undefined
}

beforeEach(() => {
  localStorage.clear()
  vi.resetAllMocks()
  vi.restoreAllMocks()
})
