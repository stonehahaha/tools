# PDF Team Splitter Payload Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the PDF team splitter view working while aligning the payload fields and download filename with the snake_case `.zip` contract.

**Architecture:** The view still owns the request payload; we add a small helper so optional inputs map to the backend’s snake_case keys before creating the `FormData`. The API helper handles the download filename. Each change is localized to the files already involved in the flow, keeping behaviors isolated and testable.

**Tech Stack:** Vue 3 + `<script setup>`, Element Plus, Vite 5, Vitest for unit tests.

---

### Task 1: Update the view test expectations

**Files:**
- Modify: `src/views/pdf-team-splitter/__tests__/index.test.ts`

- [ ] **Step 1: Write the new failing assertions**

```ts
expect(formData.get('name_column')).toBe('B')
expect(formData.get('team_column')).toBe('C')
expect(formData.get('fuzzy_threshold')).toBe('80')
expect(downloadSpy).toHaveBeenCalledWith(blob, 'pdf-team-split-result.zip')
```

- [ ] **Step 2: Run the targeted test to capture the failure**

```
npm run test -- src/views/pdf-team-splitter/__tests__/index.test.ts
```

Expected failure: assertions for `name_column`, `team_column`, `fuzzy_threshold`, or the `.zip` filename do not pass because the current view still sends camelCase keys and `.pdf`.

- [ ] **Step 3: Save the failing test output (keep a note of the failing assertion messages).**

```
# Note the stack traces mentioning missing FormData entries or unexpected download arguments.
```

### Task 2: Send optional inputs as snake_case keys from the view

**Files:**
- Modify: `src/views/pdf-team-splitter/index.vue`

- [ ] **Step 1: Add a helper that maps the optional inputs to snake_case keys and append them to `FormData`**

```ts
const appendOptionalFields = (formData: FormData) => {
  formData.append('name_column', nameColumn.value)
  formData.append('team_column', teamColumn.value)
  formData.append('fuzzy_threshold', String(fuzzyThreshold.value))
}

const formData = new FormData()
formData.append('roster', rosterFile.value as File)
formData.append('pdf', pdfFile.value as File)
formData.append('sheet', String(sheet.value))
appendOptionalFields(formData)
```

- [ ] **Step 2: Run the targeted test to verify it still fails (because the download helper still returns `.pdf`)**

```
npm run test -- src/views/pdf-team-splitter/__tests__/index.test.ts
```

Expected failure: download filename assertion (`.zip`) still pending.

- [ ] **Step 3: Confirm helper logic covers the existing defaults (`B`, `C`, `80`).**

### Task 3: Update the download helper to emit `.zip`

**Files:**
- Modify: `src/api/pdfTeamSplit.ts`

- [ ] **Step 1: Change the default download filename**

```ts
link.download = filename ?? 'pdf-team-split-result.zip'
```

- [ ] **Step 2: Run the targeted test to ensure everything now passes**

```
npm run test -- src/views/pdf-team-splitter/__tests__/index.test.ts
```

Expected result: Test should pass because the helper and download filename now match the assertions.

- [ ] **Step 3: Double-check no other call sites of `downloadPdfTeamSplitResult` expect `.pdf`.**

### Task 4: Final verification and commit

**Files:**
- Test: `src/views/pdf-team-splitter/__tests__/index.test.ts`

- [ ] **Step 1: Run the targeted test once more to verify clean slate**

```
npm run test -- src/views/pdf-team-splitter/__tests__/index.test.ts
```

- [ ] **Step 2: Stage the touched files**

```
git add src/api/pdfTeamSplit.ts src/views/pdf-team-splitter/index.vue src/views/pdf-team-splitter/__tests__/index.test.ts docs/superpowers/specs/2026-04-07-pdf-team-splitter-design.md docs/superpowers/plans/2026-04-07-pdf-team-splitter-plan.md
```

- [ ] **Step 3: Commit the change**

```
git commit -m "fix: align pdf team splitter payload and download"
```

### Spec Review Notes
Confirm the spec satisfies the requirements (snake_case fields, `.zip` download, updated test) before executing this plan. The plan keeps TDD intact: failing test → implementation → verification.
