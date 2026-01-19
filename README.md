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

## Data Scraper (Add a Show)
The scraper prompts you through an IMDb search, fetches details, and updates `src/data/shows.json`.

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
