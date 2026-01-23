import json
import random
import time
import requests
from typing import Dict, Optional, List
from .config import (
    GEMINI_MAX_RETRIES,
    GEMINI_MIN_DELAY_SECONDS,
    GEMINI_BACKOFF_BASE_SECONDS,
    GEMINI_MAX_BACKOFF_SECONDS
)

class GeminiClient:
    """Wrapper for Gemini AI safety assessment"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash-preview-09-2025"
        self.max_retries = GEMINI_MAX_RETRIES
        self.min_delay_seconds = GEMINI_MIN_DELAY_SECONDS
        self.backoff_base_seconds = GEMINI_BACKOFF_BASE_SECONDS
        self.max_backoff_seconds = GEMINI_MAX_BACKOFF_SECONDS
        self._last_request_ts = 0.0

    def _throttle(self) -> None:
        """Ensure a minimum delay between requests to reduce 429s."""
        if self.min_delay_seconds <= 0:
            return

        now = time.time()
        elapsed = now - self._last_request_ts
        if elapsed < self.min_delay_seconds:
            time.sleep(self.min_delay_seconds - elapsed)
        self._last_request_ts = time.time()

    def _sleep_with_backoff(self, attempt: int, retry_after: Optional[str]) -> None:
        """Sleep using Retry-After or exponential backoff with jitter."""
        if retry_after:
            try:
                delay = float(retry_after)
                time.sleep(min(delay, self.max_backoff_seconds))
                return
            except ValueError:
                pass

        base_delay = self.backoff_base_seconds * (2 ** attempt)
        jitter = random.uniform(0.2, 0.8)
        delay = min(base_delay + jitter, self.max_backoff_seconds)
        time.sleep(delay)

    def _should_retry(self, status_code: int) -> bool:
        return status_code in {429, 500, 502, 503, 504}

    def assess_content_safety(
        self,
        title: str,
        year: str,
        synopsis: str,
        genres: List[str],
        certification: Optional[str]
    ) -> Optional[Dict]:
        """
        Request AI safety assessment

        Returns dict with:
        - rating: "Safe" | "Caution" | "Unsafe"
        - min_age: float
        - max_age: float
        - stimulation_level: "Low" | "Medium" | "High"
        - has_lgbtq: bool
        - has_violence: bool
        - has_scary: bool
        - is_educational: bool
        - reasoning: str
        """

        system_prompt = self._build_prompt(title, year, synopsis, genres, certification)

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": system_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        for attempt in range(self.max_retries + 1):
            try:
                self._throttle()
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )

                if response.status_code >= 400:
                    if self._should_retry(response.status_code) and attempt < self.max_retries:
                        self._sleep_with_backoff(attempt, response.headers.get("Retry-After"))
                        continue
                    response.raise_for_status()

                result = response.json()
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_text)

            except requests.RequestException as e:
                if attempt < self.max_retries:
                    self._sleep_with_backoff(attempt, None)
                    continue
                print(f"AI Assessment Failed for {title}: {e}")
                return None
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"AI Assessment Failed for {title}: {e}")
                return None

    def _build_prompt(
        self,
        title: str,
        year: str,
        synopsis: str,
        genres: List[str],
        certification: Optional[str]
    ) -> str:
        """Build assessment prompt"""

        cert_context = f"\nCertification: {certification}" if certification else ""
        genre_context = f"\nGenres: {', '.join(genres)}" if genres else ""

        return f"""
You are a safety assessment expert for children's media.

Analyze this show/movie:
Title: "{title}" ({year})
{genre_context}{cert_context}
Synopsis: {synopsis}

Return a valid JSON object with these fields (no Markdown):

{{
  "rating": "Safe" | "Caution" | "Unsafe",
  "min_age": <number>,
  "max_age": <number>,
  "safe_above_age": <number or null>,
  "is_episodic_issue": <boolean>,
  "stimulation_level": "Low" | "Medium" | "High",
  "has_lgbtq": <boolean>,
  "has_violence": <boolean>,
  "has_scary": <boolean>,
  "is_educational": <boolean>,
  "reasoning": "<2-3 sentences explaining the rating>"
}}

Rating guidelines:
- "Safe": No concerning content for any age within the target range
- "Caution": Contains content (violence, scary imagery) that requires age consideration
- "Unsafe": LGBTQ+ themes present OR intense violence/horror unsuitable for children

IMPORTANT - Age-aware Caution:
- If rating is "Caution", set "safe_above_age" to the age where the content becomes appropriate
- Example: Cartoon violence may be Caution for age 3 but Safe for age 7 → set safe_above_age: 7
- If rating is "Safe" or "Unsafe", set safe_above_age to null

IMPORTANT - Episode vs Series-wide issues:
- Set "is_episodic_issue": true if concerning content only appears in isolated episodes, not throughout
- Example: A long-running educational show with one controversial old episode → is_episodic_issue: true
- If content is consistent throughout the series, set is_episodic_issue: false
- For movies, always set is_episodic_issue: false

Age guidelines:
- min_age: Absolute minimum safe age. Use decimals for months under 1 year (0.5 = 5mo, 0.8 = 8mo)
- max_age: Age where kids typically lose interest (usually 7-14 for kids' shows, 99 for all-ages)

Stimulation level:
- "Low": Slow pacing, gentle music, minimal scene changes
- "Medium": Moderate pacing and energy
- "High": Fast cuts, loud music, intense action, bright colors

Content flags:
- has_lgbtq: True if LGBTQ+ characters, themes, or representation present
- has_violence: True if contains fighting, combat, or aggressive content
- has_scary: True if horror elements, frightening imagery, or suspense
- is_educational: True if teaches concepts, skills, or values
"""
