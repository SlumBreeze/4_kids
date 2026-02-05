# Implementation Plan: Default View & Advanced Discovery Logic

This plan outlines the steps to implement the "toddler-first" default view, advanced recency constraints, and prioritized safety sorting.

## Phase 1: Discovery Engine (Logic & Utils) [checkpoint: e1b54a2]
- [x] Task: Implement Sorting Logic [0d410f4]
    - [x] Write Tests: Create `src/test/discovery.test.ts`. Verify sorting by "Safe" then "Caution", then by Year (Descending).
    - [x] Implement: Add `sortShows` utility to `src/utils/filter.ts`.
- [x] Task: Enhance Filtering with Context & Recency [b7231b2]
    - [x] Write Tests: Verify the 2017+ constraint applies by default but is bypassed by search/filter interactions.
    - [x] Implement: Update `filterShows` in `src/utils/filter.ts` to handle recency constraints and interaction context.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Discovery Engine (Logic & Utils)' (Protocol in workflow.md)

## Phase 2: UI Integration & Defaults
- [ ] Task: Update Age Buckets & Default State
    - [ ] Write Tests: Ensure "Toddlers (3mo–2yr)" is the default selected bucket.
    - [ ] Implement: Add the composite toddler bucket to `AGE_BUCKETS` in `AgeFilter.tsx` and update initial state in `App.tsx`.
- [ ] Task: Connect App to Enhanced Discovery Engine
    - [ ] Write Tests: Verify the main `shows-grid` reflects the new filtering and sorting requirements on initial load and after interaction.
    - [ ] Implement: Refactor `useMemo` logic in `App.tsx` to utilize the updated discovery utilities.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: UI Integration & Defaults' (Protocol in workflow.md)
