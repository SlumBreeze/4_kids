# Implementation Plan - Search Bypass Filters

This plan outlines the steps to allow the search functionality to bypass all active filters and safety classifications when a search term is present.

## Phase 1: Core Logic Implementation (TDD)
This phase focuses on modifying the filtering logic to prioritize search terms over existing filters.

- [x] Task: Create unit tests for search bypass logic [1b3c943]
    - [x] Create `src/test/searchBypass.test.ts`
    - [x] Define tests: "Search bypasses age filter"
    - [x] Define tests: "Search bypasses stimulation filter"
    - [x] Define tests: "Search bypasses release year (toddler-first) filter"
    - [x] Define tests: "Clearing search restores filter application"
- [x] Task: Implement Search Bypass in filtering utility [1b3c943]
    - [x] Modify `src/utils/filter.ts` (or the relevant filter hook in `App.tsx`) to check if `searchQuery` is non-empty.
    - [x] If `searchQuery` is active, return results based solely on title matching.
    - [x] Ensure `classifyShow` or equivalent logic is bypassed or handled as per spec (Option A).
- [x] Task: Refactor and Verify Coverage [1b3c943]
    - [x] Refactor filtering logic for clarity.
    - [x] Ensure >80% coverage for the new logic.
- [ ] Task: Conductor - User Manual Verification 'Core Logic Implementation' (Protocol in workflow.md)

## Phase 2: UI Visual Feedback
This phase adds the visual cues to indicate when filters are being bypassed.

- [ ] Task: Create UI tests for visual feedback
    - [ ] Add tests to `src/test/Filters.test.tsx` to verify CSS classes are applied when search is active.
- [ ] Task: Implement "Gray out" effect for filters
    - [ ] Add a `searching` state or derive it from `searchQuery` in `App.tsx`.
    - [ ] Pass a `disabled` or `isDimmed` prop to `AgeFilter` and `StimulationFilter` components.
    - [ ] Update `AgeFilter.module.css` and `StimulationFilter.module.css` to handle the dimmed state (reduced opacity).
- [ ] Task: Conductor - User Manual Verification 'UI Visual Feedback' (Protocol in workflow.md)

## Phase 3: Integration & Relevance Sorting
Final adjustments to ensure results are sorted correctly and the UX is seamless.

- [ ] Task: Implement Relevance Sorting
    - [ ] Ensure the search result list is sorted by title relevance when search is active.
- [ ] Task: Final Integration Check
    - [ ] Verify state restoration when search is cleared.
    - [ ] Perform a full smoke test of the application.
- [ ] Task: Conductor - User Manual Verification 'Integration & Relevance Sorting' (Protocol in workflow.md)
