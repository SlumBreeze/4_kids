# Technology Stack: KidShow Scout

## Frontend
- **Framework:** React 18 (Functional components, Hooks)
- **Language:** TypeScript (Strict mode)
- **Build Tool:** Vite 5
- **Styling:** CSS Modules for component-scoped styles, with Global CSS for resets and theme variables.
- **State Management:** React Component State (Prop drilling/Context where appropriate).

## Data Pipeline (Python)
- **Language:** Python 3.x
- **Core Libraries:**
    - `requests`: For fetching data from external APIs (TMDB).
    - `beautifulsoup4`: For legacy web scraping needs.
    - `rich`: For enhanced CLI formatting during the review process.
    - `python-dotenv`: For managing API keys and environment variables.
- **AI Integration:** Google Gemini API (via `google-generativeai`) for content safety assessment and tagging.

## Storage & Data
- **Primary Database:** `src/data/shows.json` (Flat JSON file).
- **Staging:** `scripts/data/tmdb_staging/` (JSON files for multi-stage pipeline state).

## Development Tools
- **Linting:** ESLint (Flat Config) with TypeScript and React plugins.
- **Formatting:** Prettier (assumed or inferred via project standards).
- **Version Control:** Git.
