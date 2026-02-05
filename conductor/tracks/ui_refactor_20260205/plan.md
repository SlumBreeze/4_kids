# Implementation Plan: UI Refactor to Product Guidelines

This plan outlines the steps to refactor the KidShow Scout frontend to align with the new Product Guidelines, focusing on a playful, safety-first aesthetic.

## Phase 1: Foundation & Theme Setup [checkpoint: edd8043]
- [x] Task: Define Global CSS Variables (Colors, Border Radius) [8f7bd60]
    - [x] Write Tests: Ensure theme variables are present in the CSS.
    - [x] Implement: Update `src/index.css` with the vibrant palette and `1.5rem` border-radius variable.
- [x] Task: Integrate Playful Typography [cb6589c]
    - [x] Write Tests: Verify the font-family is correctly applied to the body.
    - [x] Implement: Load "Fredoka" or "Quicksand" from Google Fonts and set as the default sans-serif.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Theme Setup' (Protocol in workflow.md)

## Phase 2: Core Components Refactor
- [x] Task: Refactor ShowCard Component [b1ac971]
    - [x] Write Tests: Ensure ShowCard uses the new border-radius and vibrant styling.
    - [x] Implement: Update `ShowCard.tsx` and `ShowCard.module.css`.
- [x] Task: Refactor Filter Components (Age & Stimulation) [8f46fb5]
    - [x] Write Tests: Verify filters have rounded edges and clear active states.
    - [x] Implement: Update `AgeFilter.tsx`, `StimulationFilter.tsx` and their modules.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Components Refactor' (Protocol in workflow.md)

## Phase 3: Detail View & Modals
- [ ] Task: Refactor ShowDetailModal
    - [ ] Write Tests: Ensure modal has soft edges and clean, rounded typography.
    - [ ] Implement: Update `ShowDetailModal.tsx` and `ShowDetailModal.module.css`.
- [ ] Task: Implement Safety Status Badges
    - [ ] Write Tests: Verify badges use high-contrast color coding (Safe/Caution/Unsafe).
    - [ ] Implement: Create a shared Badge component or update existing status indicators.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Detail View & Modals' (Protocol in workflow.md)
