# Data Processing Favicon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current browser-tab icon with a favicon-specific SVG that follows the approved “流程线 + 蓝紫渐变” direction and keep the page title as `数据处理`.

**Architecture:** Keep the change isolated to browser-entry assets. Add one dedicated favicon SVG in `public/`, point `index.html` at it, and add a small file-level regression test that verifies the title, icon href, and asset existence. Finish by running the existing build to confirm the asset is emitted correctly.

**Tech Stack:** Vite, Vitest, TypeScript, SVG

---

## Planned File Layout

- `public/favicon-data-processing.svg`
  Dedicated small-size favicon asset for browser tabs.
- `index.html`
  Browser-tab title and favicon reference.
- `test/favicon.test.ts`
  File-level regression test for the title/icon wiring.

### Task 1: Add Favicon Regression Test

**Files:**
- Create: `test/favicon.test.ts`

- [ ] **Step 1: Write the failing favicon test**

Create `test/favicon.test.ts` with:

```ts
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

describe('favicon entrypoint', () => {
  it('uses the dedicated data-processing favicon asset', () => {
    const projectRoot = process.cwd()
    const html = readFileSync(resolve(projectRoot, 'index.html'), 'utf8')

    expect(html).toContain('<title>数据处理</title>')
    expect(html).toContain('href="/favicon-data-processing.svg"')
    expect(existsSync(resolve(projectRoot, 'public', 'favicon-data-processing.svg'))).toBe(true)
  })
})
```

- [ ] **Step 2: Run the favicon test and confirm it fails**

Run:

```powershell
npm run test -- test/favicon.test.ts
```

Expected: FAIL because `index.html` still points at the old icon path and the dedicated favicon asset does not exist yet.

### Task 2: Create The Favicon Asset And Wire It In

**Files:**
- Create: `public/favicon-data-processing.svg`
- Modify: `index.html`

- [ ] **Step 1: Create the new favicon SVG**

Create `public/favicon-data-processing.svg` with:

```svg
<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="8" y1="6" x2="56" y2="58" gradientUnits="userSpaceOnUse">
      <stop stop-color="#667EEA"/>
      <stop offset="1" stop-color="#7C5CFF"/>
    </linearGradient>
  </defs>
  <rect x="4" y="4" width="56" height="56" rx="16" fill="url(#bg)"/>
  <path d="M18 20L46 32L18 44" stroke="white" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M18 20H34" stroke="white" stroke-width="4.5" stroke-linecap="round"/>
  <path d="M18 44H34" stroke="white" stroke-width="4.5" stroke-linecap="round"/>
  <circle cx="18" cy="20" r="4.5" fill="#FFD166"/>
  <circle cx="46" cy="32" r="4.5" fill="#FFD166"/>
  <circle cx="18" cy="44" r="4.5" fill="#FFD166"/>
</svg>
```

- [ ] **Step 2: Point `index.html` at the new favicon**

Update the `<head>` in `index.html` to:

```html
<head>
  <meta charset="UTF-8">
  <link rel="icon" type="image/svg+xml" href="/favicon-data-processing.svg">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>数据处理</title>
</head>
```

- [ ] **Step 3: Re-run the favicon test and confirm it passes**

Run:

```powershell
npm run test -- test/favicon.test.ts
```

Expected: `1 passed`

- [ ] **Step 4: Commit the favicon asset wiring**

```powershell
git add public/favicon-data-processing.svg index.html test/favicon.test.ts
git commit -m "feat: add dedicated data processing favicon"
```

### Task 3: Verify Production Build

**Files:**
- No additional file changes expected

- [ ] **Step 1: Run the full build verification**

Run:

```powershell
npm run build
```

Expected: Vite build completes successfully and emits the favicon reference into the final `dist/index.html`.

- [ ] **Step 2: Spot-check the built HTML**

Run:

```powershell
Get-Content dist/index.html
```

Expected: built HTML contains `favicon-data-processing.svg` and `<title>数据处理</title>`.

## Spec Coverage Check

- Dedicated favicon instead of the oversized original asset: covered by Task 2.
- Approved “流程线 + 蓝紫渐变” direction: covered by Task 2 SVG content.
- Browser tab title remains `数据处理`: covered by Tasks 1 and 2.
- Build validation for deployment safety: covered by Task 3.

## Execution Notes

- Keep this implementation limited to browser-tab assets; do not modify the in-app brand block or other logos.
- If the final favicon still feels visually small in the browser, iterate on the SVG proportions rather than swapping formats first.
