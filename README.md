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

Automatically discovers, enriches, and rule-assesses kids' shows from TMDB.

```bash
# Install Python dependencies
python -m pip install -r scripts/requirements.txt
```

Required `.env` at project root:
```
TMDB_API_KEY=your_key_here
```

```bash
# Stage 1: Discover content from TMDB (~2 min)
npm run tmdb:discover

# Stage 2: Enrich with full metadata (~5 min, rate-limited)
npm run tmdb:enrich

# Stage 3: Rule-based safety assessment
npm run tmdb:assess

# Stage 4: Human review (interactive)
npm run tmdb:review

# Stage 4 (automated): Accept all pending, cap maxAge at 5
npm run tmdb:auto

# Stage 5: Import approved shows into shows.json
npm run tmdb:import

# Stage 5 (automated): Import using ID matches only, preserving title variants
npm run tmdb:import:auto

# Refresh existing TMDB-backed records and write a report only
npm run tmdb:refresh

# Apply the refresh report to shows.json
npm run tmdb:refresh:apply

# Audit duplicate IDs and possible title variants
npm run tmdb:audit-variants

# Check free fallback sources for missing metadata suggestions
npm run tmdb:free-sources

# Shortcut: Run Stages 1–3 sequentially
npm run tmdb:full

# Full automated sync: discover, enrich, assess, auto-review, import, refresh, audit
npm run tmdb:sync

# Pipeline runner: content stages + audit stages
npm run tmdb:pipeline

# Content only: discover, enrich, assess, auto-review, import
npm run tmdb:pipeline:content

# Audit only: refresh report, variant audit, free-source report
npm run tmdb:pipeline:audit

# Preview the planned pipeline stages without running API calls
npm run tmdb:pipeline:plan
```

**Staging files** (in `scripts/data/tmdb_staging/`):

| File | Contents |
|------|----------|
| `1_discovered.json` | Raw TMDB results |
| `2_enriched.json` | Full metadata + IMDb IDs |
| `3_assessed.json` | Rule-based safety assessments |
| `4_reviewed.json` | Human-approved items |
| `7_refresh_report.json` | Existing-record metadata changes from TMDB |
| `8_variant_audit.json` | Duplicate-ID and likely-variant report |
| `9_free_source_report.json` | TVmaze/Wikidata fallback suggestions |

Title variants are intentionally preserved. For example, `Little Baby Bum` and `Little Baby Bum: Music Time` should remain separate records when their source IDs differ. Automated import no longer replaces a record by title unless `python scripts/tmdb/5_import.py --match-title` is used explicitly.

Free fallback sources are report-only. TVmaze and Wikidata suggestions are useful for filling missing fields or cross-checking records, but they do not overwrite `shows.json` automatically.

Rule-based assessment is deterministic and auditable. It uses certification, genres, title text, and synopsis text to flag content categories such as violence, scary imagery, educational content, and explicit LGBTQ-related terms. It cannot prove absence; flagged or important records still need human review.

Precision note: there is no reliable free public database that proves a kids' show has no LGBTQ-related content. The free, non-AI path is to use deterministic evidence flags, import only source-backed metadata, and manually review flagged titles. That is slower than pretending a model is an oracle, but it is also less stupid.

The pipeline runner lives at `scripts/tmdb/10_run_pipeline.py`. It is the preferred automation entry point because it separates content acquisition from auditing and supports dry runs. By default, audit refreshes are report-only; use `python scripts/tmdb/10_run_pipeline.py --mode audit --apply-refresh` only when you intentionally want TMDB metadata refreshes written to `shows.json`.

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

- Searches IMDb, scrapes metadata, and prompts for manual safety rating
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
