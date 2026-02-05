# Implementation Plan: Simplified Age Discovery

## Phase 1: Age Filter Refactor
- [x] Task: Redefine Age Buckets [807f045]
    - [x] Write Tests: Update `src/test/AgeFilter.test.ts` to verify the 4 new categories and absence of "All Ages".
    - [x] Implement: Update `AGE_BUCKETS` in `AgeFilter.tsx`.
- [x] Task: Update App Default State [be0c954]
    - [x] Write Tests: Verify `App.tsx` initializes with the Toddler bucket.
    - [x] Implement: Ensure the first bucket is the default and remove "All Ages" checks.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Age Filter Refactor' (Protocol in workflow.md)

## Phase 2: Logic Refinement [checkpoint: eeffdec]
- [x] Task: Tighten Default Discovery Logic [b7231b2]
    - [x] Write Tests: Ensure only shows matching the active bucket (especially the default toddler one) appear.
    - [x] Implement: Refine the filtering logic in `App.tsx` to handle the removal of "All Ages" and enforce strict bucket matches.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Logic Refinement' (Protocol in workflow.md)