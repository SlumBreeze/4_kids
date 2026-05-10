from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


@dataclass
class MetadataSuggestion:
    source: str
    title: str
    imdb_id: Optional[str] = None
    summary: str = ""
    image_url: str = ""
    runtime: str = ""
    genres: List[str] = None
    official_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "imdbId": self.imdb_id,
            "summary": self.summary,
            "imageUrl": self.image_url,
            "runtime": self.runtime,
            "genres": self.genres or [],
            "officialUrl": self.official_url,
        }


class TVMazeAdapter:
    source = "tvmaze"
    base_url = "https://api.tvmaze.com"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "KidShow Scout metadata updater"})

    def lookup(self, title: str) -> Optional[MetadataSuggestion]:
        response = self.session.get(
            f"{self.base_url}/singlesearch/shows",
            params={"q": title},
            timeout=10,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        externals = data.get("externals") or {}
        image = data.get("image") or {}
        runtime = data.get("averageRuntime") or data.get("runtime") or ""
        runtime_text = f"{runtime} min" if runtime else ""
        return MetadataSuggestion(
            source=self.source,
            title=data.get("name") or title,
            imdb_id=externals.get("imdb"),
            summary=data.get("summary") or "",
            image_url=image.get("original") or image.get("medium") or "",
            runtime=runtime_text,
            genres=data.get("genres") or [],
            official_url=data.get("url") or "",
        )


class WikidataAdapter:
    source = "wikidata"
    endpoint = "https://query.wikidata.org/sparql"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/sparql-results+json",
                "User-Agent": "KidShow Scout metadata updater",
            }
        )

    def lookup_by_imdb(self, imdb_id: str) -> Optional[MetadataSuggestion]:
        if not imdb_id:
            return None

        query = f"""
        SELECT ?item ?itemLabel ?official ?genreLabel WHERE {{
          ?item wdt:P345 "{imdb_id}".
          OPTIONAL {{ ?item wdt:P856 ?official. }}
          OPTIONAL {{ ?item wdt:P136 ?genre. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 20
        """
        response = self.session.get(
            self.endpoint,
            params={"query": query, "format": "json"},
            timeout=20,
        )
        response.raise_for_status()
        bindings = response.json().get("results", {}).get("bindings", [])
        if not bindings:
            return None

        title = bindings[0].get("itemLabel", {}).get("value") or ""
        official = bindings[0].get("official", {}).get("value") or ""
        genres = sorted(
            {
                binding.get("genreLabel", {}).get("value")
                for binding in bindings
                if binding.get("genreLabel", {}).get("value")
            }
        )
        return MetadataSuggestion(
            source=self.source,
            title=title,
            imdb_id=imdb_id,
            genres=genres,
            official_url=official,
        )
