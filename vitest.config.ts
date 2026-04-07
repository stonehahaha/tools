import { mergeConfig } from 'vite'
import baseViteConfig from './vite.config'
import { defineConfig } from 'vitest/config'

const vitestConfig = mergeConfig(baseViteConfig, {
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./test/setup.ts'],
    deps: {
      inline: ['element-plus', '@element-plus/icons-vue'],
    },
    passWithNoTests: true,
  },
})

export default defineConfig(vitestConfig)
