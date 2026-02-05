# Specification: Default View & Simplified Age Groups

## Overview
Refine the discovery interface to use broad age categories instead of granular month/year buckets. Ensure the application defaults strictly to the "Toddler" view on load.

## Functional Requirements
### 1. Simplified Age Groups
- Remove "All Ages" filter.
- Remove granular number-based filters (3-5mo, 1-2yr, etc.).
- Implement the following broad categories:
    - **Toddlers (3mo–2yr)** [Default]
    - **Preschoolers (3–5yr)**
    - **School Age (6–9yr)**
    - **Pre-Teens (10–12yr)**

### 2. Default State & Filtering
- On initial load, the **"Toddlers (3mo–2yr)"** filter is active.
- **Strict Default View:** Only shows appropriate for the 3mo–2yr range (minAge <= 2.0 && maxAge >= 0.3) released in **2017 or newer** are shown.
- Selection of any other age category ignores the 2017+ recency constraint.

### 3. Search Behavior
- Search continues to bypass all age and recency constraints to ensure full database discoverability.

## Success Criteria
- The age filter bar shows 4 clean category buttons.
- No "All Ages" button is present.
- The app loads with only recent toddler content visible.