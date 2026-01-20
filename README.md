# KidShow Scout

KidShow Scout is a small React + TypeScript app that helps parents find age-appropriate TV shows. It ships as a Vite SPA and includes a lightweight data ingestion script to add new titles from IMDb.

## Features
- Search and filter shows by age bucket.
- Detail modal with ratings, tags, and context.
- JSON-backed data in `src/data/shows.json`.

## Tech Stack
- React 18 + TypeScript
- Vite 5
- ESLint (flat config)

## Getting Started
```bash
npm install
npm run dev
```
Open the URL printed by Vite (usually `http://localhost:5173`).

## Useful Commands
```bash
npm run dev      # start dev server with HMR
npm run build    # type-check and build for production
npm run preview  # preview the production build locally
npm run lint     # run ESLint
```

## Data Ingestion

### TMDB Batch Pipeline (Recommended)
The TMDB pipeline automatically discovers, enriches, and assesses hundreds of kids' shows from TMDB with AI-powered safety ratings.

**Prerequisites:**
```bash
# Install Python dependencies
python -m pip install -r scripts/requirements.txt

# TMDB API key should already be in .env
# If not, add it: TMDB_API_KEY=your_key_here
```

**Run the Pipeline:**
```bash
# Stage 1: Discover content from TMDB (~2 min)
python scripts/tmdb/1_discover.py

# Stage 2: Enrich with full metadata (~5 min, rate-limited)
python scripts/tmdb/2_enrich.py

# Stage 3: AI safety assessment (~3 min)
python scripts/tmdb/3_assess.py

# Stage 4: Human review (interactive, user-paced)
python scripts/tmdb/4_review.py

# Stage 5: Import approved shows to shows.json (~5 sec)
python scripts/tmdb/5_import.py
```

**Pipeline Features:**
- Discovers 100+ kids shows from Netflix, Disney+, Hulu
- AI-powered safety ratings and age recommendations
- Interactive CLI review queue with accept/edit/reject options
- Tracks TMDB ID and streaming platform availability
- Resumable from any stage (each stage saves to staging files)

**Staging Files:**
- `scripts/data/tmdb_staging/1_discovered.json` - Raw TMDB results
- `scripts/data/tmdb_staging/2_enriched.json` - Full metadata + IMDb IDs
- `scripts/data/tmdb_staging/3_assessed.json` - AI safety assessments
- `scripts/data/tmdb_staging/4_reviewed.json` - Human-approved items

### Manual Data Scraper (Legacy, for single shows)
The legacy IMDb scraper prompts you through a manual search and updates `src/data/shows.json`.

1) Install Python dependencies:
```bash
python -m pip install -r scripts/requirements.txt
```

2) Run the interactive script:
```bash
python scripts/add_show.py
```

Notes:
- The script can overwrite existing entries if you confirm.
- It auto-scrapes description, runtime, image, and year range when available.
- Ages in the scraper use a compact format: whole numbers are years, decimals under 1 are months (e.g. `0.5` means 5 months).
- If you see `ModuleNotFoundError`, install dependencies with
  `python -m pip install -r scripts/requirements.txt` or use a virtual env.

## Project Structure
- `src/` app code and styles
- `src/components/` reusable UI components
- `src/utils/` shared helpers
- `src/data/` show data (`shows.json`)
- `public/` static assets
- `scripts/` data ingestion tools

## Contributing
See `AGENTS.md` for repo-specific guidelines.
