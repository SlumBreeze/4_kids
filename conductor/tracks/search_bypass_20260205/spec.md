# Specification: Search Bypass Filters

## Overview
Currently, the search functionality in KidShow Scout is constrained by active filters (Age, Stimulation, and the default "toddler-first" release year filter). This track introduces a "Power Search" behavior where typing in the search bar automatically bypasses all filters and safety classifications to show all matching content in the database.

## Functional Requirements
- **Automatic Bypass**: When the search input is non-empty, all active filters (Age, Stimulation level) and the default release year filter (2017+) must be ignored.
- **Full Database Search**: Search results must include shows regardless of their safety rating (`Safe`, `Caution`, `Unsafe`) or age recommendation.
- **State Restoration**: When the search input is cleared, the application must immediately restore the previously active filters and the "toddler-first" view.
- **Relevance Sorting**: Search results should be sorted primarily by title relevance to the search query.

## UI/UX Requirements
- **Visual Feedback**: While searching (input is non-empty), the Filter UI sections (Age Buckets and Stimulation Levels) should have their opacity reduced (grayed out) to indicate they are currently inactive.
- **Filter Interaction**: (Optional/Implicit) While filters are grayed out, they should ideally be non-interactive to prevent confusion, although simply ignoring them in the logic is the primary goal.

## Acceptance Criteria
- [ ] Typing "Cocomelon" shows the show even if the "High Stimulation" filter is NOT selected (assuming Cocomelon is tagged as High).
- [ ] Typing a search term shows content released before 2017 (bypassing the default filter).
- [ ] Clearing the search bar restores the results to only shows matching the active Age/Stimulation filters.
- [ ] The Filter sidebar/header visually dims when search text is present.

## Out of Scope
- Adding new search algorithms (e.g., fuzzy search) beyond existing title matching.
- Changing how shows are stored or assessed in the backend.
