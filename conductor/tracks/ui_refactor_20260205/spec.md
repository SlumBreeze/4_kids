# Specification: UI Refactor to Product Guidelines

## Overview
This track focuses on updating the existing KidShow Scout UI to match the newly established Product Guidelines. This includes implementing rounded shapes, a vibrant color palette, and playful typography.

## Requirements
- **Rounded Shapes:** Update all major UI components (ShowCard, AgeFilter, StimulationFilter, ShowDetailModal) to use large border radii (min `1.5rem`).
- **Typography:** Integrate and apply rounded sans-serif fonts (e.g., Fredoka or Quicksand) for headers and UI text.
- **Color Palette:** Implement the vibrant primary color palette (Yellows, Blues, Purples) as CSS variables.
- **Consistency:** Ensure all components use the new visual language consistently.

## Technical Details
- **CSS Modules:** Modifications should be made within the existing `*.module.css` files.
- **Global CSS:** Theme variables (colors, border-radius) should be defined in `src/index.css`.
- **Fonts:** Use standard web font loading techniques (Google Fonts or local assets).

## Success Criteria
- All buttons, cards, and modals have rounded corners per the guidelines.
- The font has been changed to a rounded sans-serif.
- The color scheme reflects the approved vibrant palette.
- UI remains functional and responsive.
