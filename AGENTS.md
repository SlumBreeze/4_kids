# Repository Guidelines

## Project Structure & Module Organization
- `src/` holds the React + TypeScript app. Core UI lives in `src/App.tsx`.
- `src/components/` contains UI components with co-located CSS modules.
- `src/utils/` includes shared helpers like `filter.ts` and `format.ts`.
- `src/data/` stores show data (`shows.json`) and mock data (`mockShows.ts`).
- `public/` hosts static assets (e.g., `public/assets/mascots.png`).
- `scripts/` contains Python data tooling (see `scripts/add_show.py`).
- `dist/` is the Vite build output (generated).

## Build, Test, and Development Commands
- `npm install` installs dependencies.
- `npm run dev` starts the Vite dev server with HMR.
- `npm run build` type-checks and builds the production bundle.
- `npm run preview` serves the production build locally.
- `npm run lint` runs ESLint on the codebase.

## Coding Style & Naming Conventions
- Indentation: 2 spaces; use semicolons and double quotes (see `src/App.tsx`).
- React components use PascalCase in `src/components/` (e.g., `ShowCard.tsx`).
- CSS Modules use `ComponentName.module.css` naming.
- ESLint is configured in `eslint.config.js`; run it before submitting.

## Testing Guidelines
- No automated test framework is configured yet.
- For changes, verify key flows manually via `npm run dev`:
  search, age filtering, and opening/closing the detail modal.
- If you add tests, document the runner and add the command here.

## Commit & Pull Request Guidelines
- Commit messages in this repo use short, imperative summaries
  (examples: "Remove all mock data", "Automate year/runtime scraping").
- PRs should include: concise description, relevant issue links,
  and screenshots for UI changes.
- Include a short list of manual test steps (e.g., "Search for 'Bluey'").

## Data & Script Notes
- Python tooling depends on `scripts/requirements.txt`.
- Keep `src/data/shows.json` consistent with any updates made by scripts.
