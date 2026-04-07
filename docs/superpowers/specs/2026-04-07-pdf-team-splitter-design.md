# PDF Team Splitter Optional Field Mapping

## Overview
The PDF team splitter view already lets users upload a roster and a PDF, then optionally tweak the name column, team column, and fuzzy threshold before generating a team-split result. The backend now expects those optional fields to be submitted under snake_case keys, and the generated archive should download as a `.zip` instead of a `.pdf`. We need to update the frontend payload builder, the download helper, and the view test to keep the UI behavior the same while satisfying the new API contract.

## Requirements
- Send the optional inputs (`name`, `team`, `fuzzy threshold`) under the request keys `name_column`, `team_column`, and `fuzzy_threshold`.
- Keep `sheet` (mandatory) untouched, continue posting roster + PDF files as files.
- Make the download helper emit a `.zip` filename so the browser gives the archive the correct extension.
- Update the existing view-level test to trust the snake_case field names and new filename.
- Do not change any other interactions, labels, or styles.
- Continue relying on the existing `requestPdfTeamSplit` / `downloadPdfTeamSplitResult` helpers.
- TDD: update the test first to assert the new expectations, run it, then implement the code changes.

## Approaches
1. **Minimal form patch**
   - Keep `submitSplit` as-is and just rename the `FormData` keys and download filename.
   - Pros: Lowest code churn, easiest to validate via glance.
   - Cons: The mapping is embedded directly in the submit handler, so future changes to backend naming require touching the component.
2. **Field-map helper**
   - Extract a small helper in `index.vue` that mirrors the optional inputs to their snake_case keys before appending to `FormData`. The handler calls the helper to keep the mapping centralized and easier to test.
   - Pros: Encapsulates the name mapping and makes tests easier to reason about; future additions can reuse the helper.
   - Cons: Slightly more code and a new hook to maintain.
3. **Payload builder in API module**
   - Move the FormData construction entirely into `src/api/pdfTeamSplit.ts`, where the optional values get mapped before the request.
   - Pros: Keeps API contract enforcement near the fetch logic; simplifies the view even further.
   - Cons: Shifts UI state into the API layer, potentially making the view less testable and harder to reason about; more invasive change for a small payload rename.

## Recommendation
Use the **Field-map helper** approach. Create a small utility inside `index.vue` that translates the optional inputs (`nameColumn`, `teamColumn`, `fuzzyThreshold`) to their snake_case field names and appends them to the `FormData`. This keeps the view responsible for payload construction (matching current separation of concerns), but centralizes the mapping logic so the keys are obvious and unit-testable. The download filename update stays inside `pdfTeamSplit.ts` because the helper already lives there.

## Data Flow
1. User tweaks optional fields or leaves defaults (`sheet`, `nameColumn`, `teamColumn`, `fuzzyThreshold`).
2. `submitSplit` builds `FormData`, including the snake_case optional keys via the new helper, and posts via `requestPdfTeamSplit`.
3. On success, `downloadPdfTeamSplitResult` is called with the response blob and `'pdf-team-split-result.zip'`.

## Testing
- Update `src/views/pdf-team-splitter/__tests__/index.test.ts` to:
  - Assert the `FormData` includes `name_column`, `team_column`, and `fuzzy_threshold` plus the files.
  - Assert `downloadPdfTeamSplitResult` is invoked with the `.zip` filename.
  - Keep the rest of the test unchanged to ensure no regression in file upload button enabling.
- Run `npm run test -- src/views/pdf-team-splitter/__tests__/index.test.ts` as required.

## Open Questions / Assumptions
- Assume the backend still expects `sheet` and mandatory file keys with the same names.
- **Question for you:** Should we always send `name_column`, `team_column`, and `fuzzy_threshold` even when the user never touches them, or should we omit them (currently we always send them)? I will keep sending them with their defaults unless told otherwise.

## Next Steps
1. Update the view test to cover the new field names and `.zip` filename (should fail first).
2. Implement the helper + download filename change so the test passes.
3. Run the targeted test and commit changes.
