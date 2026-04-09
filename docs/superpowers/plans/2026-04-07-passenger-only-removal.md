# Passenger-Only Removal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the app to a single passenger information extraction tool.

**Architecture:** Keep the existing text formatter page as the only product surface, remove unrelated routes and mode branches, and add regression tests around the surviving behavior. Extract only the minimal test setup needed to verify router scope and passenger-only UI behavior.

**Tech Stack:** Vue 3, Vite, Vue Router, Element Plus, Vitest, Vue Test Utils

---

### Task 1: Add Test Infrastructure

**Files:**
- Modify: `package.json`
- Modify: `package-lock.json`
- Create: `vitest.config.ts`

- [ ] **Step 1: Add a test command and install the minimal test dependencies**
- [ ] **Step 2: Configure Vitest to run Vue tests in jsdom**

### Task 2: Lock the Target Behavior with Failing Tests

**Files:**
- Create: `src/router/__tests__/index.test.ts`
- Create: `src/views/text-formatter/__tests__/index.test.ts`

- [ ] **Step 1: Write a router test expecting only the text formatter route**
- [ ] **Step 2: Write a view test expecting passenger-only UI and extraction behavior**
- [ ] **Step 3: Run the tests and confirm they fail against the current code**

### Task 3: Remove Date Formatter and Basic Cleanup

**Files:**
- Modify: `src/router/index.ts`
- Modify: `src/layout/index.vue`
- Modify: `src/views/text-formatter/index.vue`
- Delete: `src/views/date-formatter/index.vue`
- Delete: `src/components/tools/DateFormatter.vue`

- [ ] **Step 1: Remove date formatter routing and set the default route to text formatter**
- [ ] **Step 2: Remove the date formatter navigation item from the layout**
- [ ] **Step 3: Collapse the text formatter page into a single passenger extraction mode**
- [ ] **Step 4: Delete the unused date formatter files**
- [ ] **Step 5: Re-run tests until they pass**

### Task 4: Update Docs and Verify

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README to describe the passenger-only tool**
- [ ] **Step 2: Run the full verification commands for tests, type-check, and build**
