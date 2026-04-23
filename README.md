# KidShow Scout

KidShow Scout helps parents of young children (ages 3 months – 5 years) find safe, age-appropriate TV shows and movies. Every title is rated for safety, stimulation level, and age suitability so parents can make confident, informed choices.

---

## For Users

> **Coming soon** — KidShow Scout is currently in development. The sections below describe the app once published.

### What It Does

- Browse curated shows filtered to your child's exact age group
- Filter by **stimulation level** (Low / Medium / High) to match your child's mood or time of day
- Search by title to quickly find a specific show
- Tap any show card to see full details: safety rating, content tags, cast, and the reasoning behind the rating

### Age Groups

| Group | Ages |
|-------|------|
| Toddlers | 3 months – 2 years |
| Preschoolers | 3 – 5 years |

### Safety Ratings

| Rating | Meaning |
|--------|---------|
| **Safe** | Appropriate with no concerns |
| **Caution** | May have mild content worth previewing |
| **Unsafe** | Not recommended for this age group |

### Stimulation Levels

| Level | When to use |
|-------|-------------|
| **Low** | Wind-down, naptime routine, calm period |
| **Medium** | Normal daytime viewing |
| **High** | Active, energetic play time |

---

## For Developers

### Tech Stack

- React 18 + TypeScript
- Vite 5
- ESLint (flat config)
- Python 3 (data ingestion scripts)

### Setup

```bash
npm install
npm run dev
```

Open the URL printed by Vite (usually `http://localhost:5173`).

### Commands

```bash
npm run dev      # start dev server with HMR
npm run build    # type-check and build for production
npm run preview  # preview production build
npm run lint     # run ESLint
```

### Age & Data Scope

The app targets **ages 3 months to 5 years**. Shows outside this range (`minAge >= 6`) are excluded from `src/data/shows.json`. When running the data pipeline, reject or adjust any show whose `minAge` is 6 or above.

Age values use a decimal format:
- Whole numbers = years (e.g. `3` = 3 years)
- Decimals under 1 = months (e.g. `0.5` = 5 months, `0.3` = 3 months)

### Data Ingestion

#### TMDB Batch Pipeline (Recommended)

Automatically discovers, enriches, and AI-assesses kids' shows from TMDB.

```bash
# Install Python dependencies
python -m pip install -r scripts/requirements.txt
```

Required `.env` at project root:
```
TMDB_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

```bash
# Stage 1: Discover content from TMDB (~2 min)
npm run tmdb:discover

# Stage 2: Enrich with full metadata (~5 min, rate-limited)
npm run tmdb:enrich

# Stage 3: AI safety assessment (~3 min)
npm run tmdb:assess

# Stage 4: Human review (interactive)
npm run tmdb:review

# Stage 4 (automated): Accept all pending, cap maxAge at 5
npm run tmdb:auto

# Stage 5: Import approved shows into shows.json
npm run tmdb:import

# Shortcut: Run Stages 1–3 sequentially
npm run tmdb:full
```

**Staging files** (in `scripts/data/tmdb_staging/`):

| File | Contents |
|------|----------|
| `1_discovered.json` | Raw TMDB results |
| `2_enriched.json` | Full metadata + IMDb IDs |
| `3_assessed.json` | AI safety assessments |
| `4_reviewed.json` | Human-approved items |

**Provider logos:**

```bash
# Downloads logos into public/assets/providers
# Requires LOGO_DEV_API_KEY in .env
python scripts/tmdb/download_provider_logos.py
```

**Clean slate reset:**

```bash
python scripts/tmdb/reset.py
```

#### Manual Scraper (Legacy — single shows)

```bash
python scripts/add_show.py
```

- Searches IMDb, scrapes metadata, calls Gemini for safety rating
- Interactive review before writing to `shows.json`
- Can overwrite an existing entry by confirming the prompt
- If `ModuleNotFoundError`, run `python -m pip install -r scripts/requirements.txt`

### Project Structure

```
src/
  components/    UI components (AgeFilter, ShowCard, ShowDetailModal, …)
  data/          shows.json — source of truth for all show data
  types/         TypeScript interfaces (Show, ContentTag, SafetyRating, …)
  utils/         filter.ts, format.ts, sort helpers
public/          static assets (cover images, provider logos)
scripts/         Python data ingestion tools
```

### Contributing

See `AGENTS.md` for repo-specific guidelines.
