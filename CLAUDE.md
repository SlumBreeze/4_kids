# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KidShow Scout is a React + TypeScript SPA that helps parents find age-appropriate TV shows. The app filters and displays show content with safety ratings, age recommendations, and stimulation levels. Data is stored in JSON and managed through a Python scraper that fetches details from IMDb.

## Development Commands

```bash
npm install          # Install dependencies
npm run dev          # Start Vite dev server with HMR (http://localhost:5173)
npm run build        # Type-check and build for production
npm run preview      # Preview production build locally
npm run lint         # Run ESLint
```

### Python Data Ingestion Script

```bash
# Install Python dependencies
python -m pip install -r scripts/requirements.txt

# Run interactive show ingestion script
python scripts/add_show.py
```

The script searches IMDb, scrapes show details, prompts for age/safety ratings via Gemini AI, and updates `src/data/shows.json`.

## Architecture

### Data Flow & Content Classification

**Critical**: The app applies content filtering policies at runtime through `src/utils/filter.ts:classifyShow()`. This function:
- Overrides safety ratings based on content tags (e.g., "LGBTQ+ Themes" → "Unsafe")
- Is called by `filterShows()` before any search/display operations
- Modifies show objects dynamically without changing the source JSON

**Data source**: `src/data/shows.json` stores all show metadata. The `mockShows` import in `App.tsx` actually loads this JSON file (via `src/data/mockShows.ts`).

### Age Representation

Ages use a decimal format where:
- Whole numbers = years (e.g., `3` = 3 years old)
- Decimals < 1 = months (e.g., `0.5` = 5 months, `0.10` = 10 months)

This format is used in:
- `Show.minAge` and `Show.maxAge` fields
- Age bucket filtering in `App.tsx`
- Python scraper input/output
- Display formatting via `src/utils/format.ts`

### Component Structure

- **App.tsx**: Main component managing search, age filtering, stimulation filtering, and show selection state
- **AgeFilter.tsx**: Predefined age buckets (0-2, 2-5, 5-10, 10+) with min/max ranges
- **StimulationFilter.tsx**: Low/Medium/High stimulation level filter
- **ShowCard.tsx**: Grid item displaying show thumbnail and basic info
- **ShowDetailModal.tsx**: Modal overlay with full show details, cast, tags, and safety reasoning

### State Management

All state is local to `App.tsx` using `useState`:
- `searchTerm`: Text search filter
- `selectedBucket`: Age range filter (from AGE_BUCKETS)
- `selectedStimulation`: Stimulation level filter
- `selectedShow`: Currently opened show modal (or null)
- `homePicks`: Memoized random selection of 6 safe shows for homepage

Filtering logic combines search term, age bucket, and stimulation level in `useMemo`.

### Styling

Uses CSS Modules for component styles (e.g., `ShowCard.module.css`). Global styles in `src/App.css` and `src/index.css`.

## Python Scraper (`scripts/add_show.py`)

### Dependencies
- `requests`, `beautifulsoup4`: IMDb scraping
- `rich`: Terminal UI (tables, prompts, panels)
- `python-dotenv`: Load `GEMINI_API_KEY` from `.env`

### Workflow
1. Search IMDb via suggest API
2. Display results table, user selects one
3. Scrape show page for description, cast, runtime, year range
4. Call Gemini API with scraped data to assess age suitability and safety
5. Prompt user to review/edit AI suggestions
6. Update or append to `src/data/shows.json`

### Key Functions
- `search_imdb(query)`: Returns list of IMDb search results
- `get_movie_details(imdb_id)`: Scrapes show page, extracts JSON-LD data
- `assess_show_with_ai(title, description)`: Calls Gemini to generate safety ratings, tags, reasoning
- `main()`: Interactive CLI flow

## Type System (`src/types/index.ts`)

**Show** interface includes:
- `id`: IMDb ID (e.g., "tt12427840")
- `title`, `synopsis`, `coverImage`, `cast`
- `tags`: Array of `ContentTag` (Educational, Fantasy, Violence, LGBTQ+ Themes, etc.)
- `rating`: "Safe" | "Caution" | "Unsafe"
- `reasoning`: Text explanation of rating
- `ageRecommendation`: Display string (e.g., "0.5-4.0")
- `minAge`, `maxAge`: Numeric age in years (decimals < 1 for months)
- `releaseYear`: String like "2018–Present" or "2020–2023"
- `runtime`: String like "22 min" or "7 min"
- `stimulationLevel`: "Low" | "Medium" | "High" (optional)

## Code Style

- Indentation: 2 spaces
- Use semicolons and double quotes
- React components: PascalCase (e.g., `ShowCard.tsx`)
- CSS Modules: `ComponentName.module.css`
- ESLint config: `eslint.config.js` (flat config format)

## Environment Variables

`.env` file at project root:
```
GEMINI_API_KEY=your_key_here
```

Required only for Python scraper (`scripts/add_show.py`).
