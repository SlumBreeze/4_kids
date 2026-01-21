# KidShow Scout

KidShow Scout is a React + TypeScript Single Page Application (SPA) designed to help parents find age-appropriate TV shows for children. It features a curated database of shows with safety ratings, age recommendations, and stimulation levels. The data is managed via a sophisticated Python-based ingestion pipeline that leverages TMDB and AI for content assessment.

## Tech Stack

### Frontend
- **Framework:** React 18
- **Language:** TypeScript (Strict)
- **Build Tool:** Vite 5
- **Styling:** CSS Modules (`*.module.css`) + Global CSS
- **Linting:** ESLint (Flat Config)

### Data & Backend (Scripts)
- **Language:** Python 3
- **Key Libraries:** `requests`, `beautifulsoup4`, `rich`, `python-dotenv`
- **Data Source:** TMDB API (The Movie Database)
- **AI Integration:** Google Gemini (for safety assessment and tagging)
- **Storage:** JSON (`src/data/shows.json`)

## Development Workflow

### Frontend

**1. Install Dependencies:**
```bash
npm install
```

**2. Start Development Server:**
```bash
npm run dev
# Accessible at http://localhost:5173
```

**3. Build for Production:**
```bash
npm run build
```

**4. Linting:**
```bash
npm run lint
```

### Data Ingestion Pipeline

The project uses a multi-stage Python pipeline to discover, enrich, and assess shows.

**Prerequisites:**
- Python 3 installed.
- Dependencies installed: `python -m pip install -r scripts/requirements.txt`.
- `.env` file in root with:
    - `TMDB_API_KEY`: For fetching show data.
    - `GEMINI_API_KEY`: For AI content assessment.
    - `LOGO_DEV_API_KEY`: (Optional) For downloading provider logos.

**Pipeline Stages (Run in `scripts/tmdb/`):**

1.  **Discover:** `python scripts/tmdb/1_discover.py` - Fetches popular content from TMDB.
2.  **Enrich:** `python scripts/tmdb/2_enrich.py` - Adds full metadata (cast, runtime, providers).
3.  **Assess:** `python scripts/tmdb/3_assess.py` - AI evaluates safety and determines tags.
4.  **Review:**
    - Interactive: `python scripts/tmdb/4_review.py`
    - Automated: `python scripts/tmdb/4_review_auto.py`
5.  **Import:** `python scripts/tmdb/5_import.py` - Merges approved shows into `src/data/shows.json`.

**Legacy Scraper:**
- Single show interactive add: `python scripts/add_show.py`

## Architecture & Conventions

### Data Model (`src/types/index.ts`)

The central `Show` interface drives the application.
- **Age Representation:**
    - **Whole numbers:** Years (e.g., `3` = 3 years).
    - **Decimals:** Months (e.g., `0.5` = 5 months, `0.10` = 10 months).
    - This format governs `minAge`, `maxAge`, and filtering logic.
- **Safety:** `rating` ("Safe" | "Caution" | "Unsafe") and `reasoning`.
- **Stimulation:** `stimulationLevel` ("Low" | "Medium" | "High").

### Runtime Filtering (`src/utils/filter.ts`)

**Critical:** The application applies strict safety policies at runtime.
- `classifyShow(show)`: Can override a show's stored rating based on specific tags (e.g., flagging "LGBTQ+ Themes" as "Unsafe" per current configuration).
- This function is invoked before search or display, ensuring policy enforcement regardless of the static JSON data.

### Component Structure (`src/components/`)

- **State Management:** `App.tsx` holds the global state (search, filters, modal selection).
- **Styling:** Components use scoped CSS Modules (e.g., `ShowCard.module.css`).
- **Filters:**
    - `AgeFilter.tsx`: Handles predefined age buckets.
    - `StimulationFilter.tsx`: Handles stimulation level toggles.

### Project Structure

```text
C:\Dev\Projects\4_kids\
├── public/              # Static assets (provider logos, etc.)
├── scripts/             # Python data ingestion tools
│   ├── tmdb/            # TMDB pipeline scripts
│   └── data/            # Staging area for pipeline data
├── src/
│   ├── components/      # React components (CSS Modules co-located)
│   ├── constants/       # App constants (Platforms, Age Buckets)
│   ├── data/            # shows.json (The Database)
│   ├── types/           # TypeScript definitions
│   ├── utils/           # Helper functions (Filtering, Formatting)
│   ├── App.tsx          # Main Application Controller
│   └── main.tsx         # Entry Point
├── package.json         # Node dependencies & scripts
└── vite.config.ts       # Vite configuration
```

## Contributing Guidelines

- **Code Style:** Follow existing patterns. Use functional components, hooks, and strict TypeScript types.
- **Data Integrity:** When modifying `shows.json` manually, respect the age decimal format and ensure all required fields are present.
- **Safety:** Do not bypass `src/utils/filter.ts` logic when adding new display features.
