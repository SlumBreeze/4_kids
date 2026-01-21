import os
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ENV_FILE = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_FILE)

# API Keys
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TMDB_WATCH_PROVIDERS = os.getenv("TMDB_WATCH_PROVIDERS", "").strip()

# Gemini tuning (rate limiting / retries)
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "5"))
GEMINI_MIN_DELAY_SECONDS = float(os.getenv("GEMINI_MIN_DELAY_SECONDS", "1.0"))
GEMINI_BACKOFF_BASE_SECONDS = float(os.getenv("GEMINI_BACKOFF_BASE_SECONDS", "2.0"))
GEMINI_MAX_BACKOFF_SECONDS = float(os.getenv("GEMINI_MAX_BACKOFF_SECONDS", "30.0"))

# API Endpoints
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

# File Paths
DATA_DIR = os.path.join(ROOT_DIR, "scripts", "data", "tmdb_staging")
os.makedirs(DATA_DIR, exist_ok=True)

DISCOVERED_FILE = os.path.join(DATA_DIR, "1_discovered.json")
ENRICHED_FILE = os.path.join(DATA_DIR, "2_enriched.json")
ASSESSED_FILE = os.path.join(DATA_DIR, "3_assessed.json")
REVIEWED_FILE = os.path.join(DATA_DIR, "4_reviewed.json")
SHOWS_FILE = os.path.join(ROOT_DIR, "src", "data", "shows.json")

# Discovery Filters
TV_DISCOVERY_FILTERS = {
    'with_watch_monetization_types': 'flatrate|free|ads',
    'watch_region': 'US',
    'with_genres': '16|10751|10762',  # Animation OR Family OR Kids
    'vote_count.gte': 5,
    'vote_average.gte': 5.0,
    'with_original_language': 'en',
    'sort_by': 'popularity.desc'
}

MOVIE_DISCOVERY_FILTERS = {
    'certification_country': 'US',
    # 'certification': 'G,PG', # Relaxing to let AI Safety (Stage 3) decide. Prevents missing unrated/mis-tagged gems.
    'with_genres': '16|10751',  # Animation OR Family
    'vote_count.gte': 5,        # Lowered from 10 to match TV
    'vote_average.gte': 5.0,
    'with_original_language': 'en',
    'sort_by': 'popularity.desc'
}

if TMDB_WATCH_PROVIDERS:
    TV_DISCOVERY_FILTERS['with_watch_providers'] = TMDB_WATCH_PROVIDERS
    MOVIE_DISCOVERY_FILTERS['with_watch_providers'] = TMDB_WATCH_PROVIDERS
