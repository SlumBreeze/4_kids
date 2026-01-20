import requests
import time
from typing import List, Dict, Optional

class TMDBClient:
    """Wrapper for TMDB API v3"""

    def __init__(self, api_key: str, base_url: str, image_base: str):
        self.api_key = api_key
        self.base_url = base_url
        self.image_base = image_base
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.25  # 250ms = ~4 req/sec

    def _rate_limit(self):
        """Enforce rate limiting: 40 req/10s"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make rate-limited API request"""
        self._rate_limit()

        params = params or {}
        params['api_key'] = self.api_key

        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def discover_tv(self, page: int = 1, **filters) -> Dict:
        """
        Discover TV shows with filters

        Common filters:
        - with_genres: "16,10751,10762" (Animation, Family, Kids)
        - first_air_date.gte: "2015-01-01"
        - vote_count.gte: 50
        - with_watch_providers: "8|337|387" (Netflix|Disney+|Hulu)
        - watch_region: "US"
        - with_original_language: "en"
        """
        params = {'page': page, **filters}
        return self._request('/discover/tv', params)

    def discover_movies(self, page: int = 1, **filters) -> Dict:
        """
        Discover movies with filters

        Common filters:
        - with_genres: "16,10751" (Animation, Family)
        - certification_country: "US"
        - certification: "G,PG"
        - release_date.gte: "2015-01-01"
        - vote_count.gte: 100
        """
        params = {'page': page, **filters}
        return self._request('/discover/movie', params)

    def get_tv_details(self, tv_id: int) -> Dict:
        """Get full TV show details including external IDs"""
        details = self._request(f'/tv/{tv_id}', {
            'append_to_response': 'external_ids,content_ratings,watch/providers,credits'
        })
        return details

    def get_movie_details(self, movie_id: int) -> Dict:
        """Get full movie details including external IDs"""
        details = self._request(f'/movie/{movie_id}', {
            'append_to_response': 'external_ids,release_dates,watch/providers,credits'
        })
        return details

    def get_image_url(self, path: Optional[str], size: str = "w500") -> str:
        """Convert image path to full URL"""
        if not path:
            return ""
        return f"{self.image_base}/{size}{path}"

    def extract_platforms(self, providers_data: Dict) -> List[str]:
        """Extract streaming platform names from watch/providers"""
        platforms = []
        us_data = providers_data.get('results', {}).get('US', {})

        for provider_type in ['flatrate', 'free', 'ads']:
            for provider in us_data.get(provider_type, []):
                name = provider.get('provider_name')
                if name and name not in platforms:
                    platforms.append(name)

        return platforms

    def extract_certification(self, ratings_data: Dict, media_type: str) -> Optional[str]:
        """Extract US certification (TV-Y, G, PG, etc.)"""
        if media_type == 'tv':
            for rating in ratings_data.get('results', []):
                if rating.get('iso_3166_1') == 'US':
                    return rating.get('rating')
        else:  # movie
            for country in ratings_data.get('results', []):
                if country.get('iso_3166_1') == 'US':
                    for cert in country.get('release_dates', []):
                        if cert.get('certification'):
                            return cert['certification']
        return None

    def format_runtime(self, minutes: Optional[int]) -> str:
        """Convert runtime minutes to display format"""
        if not minutes:
            return ""
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            if mins > 0:
                return f"{hours} hr {mins} min"
            return f"{hours} hr"
        return f"{mins} min"

    def format_year_range(self, details: Dict, media_type: str) -> str:
        """Extract release year or year range"""
        if media_type == 'tv':
            first_air = details.get('first_air_date', '')
            last_air = details.get('last_air_date', '')
            status = details.get('status', '')

            if not first_air:
                return ""

            start_year = first_air[:4]

            if status == 'Ended' and last_air:
                end_year = last_air[:4]
                if start_year == end_year:
                    return start_year
                return f"{start_year}–{end_year}"
            else:
                return f"{start_year}–Present"
        else:  # movie
            release = details.get('release_date', '')
            return release[:4] if release else ""
