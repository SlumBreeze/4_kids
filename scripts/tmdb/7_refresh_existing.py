import argparse
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.progress import track
from rich.table import Table

from shared.config import (
    SHOWS_FILE,
    TMDB_API_KEY,
    TMDB_BASE_URL,
    TMDB_IMAGE_BASE,
    DATA_DIR,
)
from shared.enrichment import enrich_from_tmdb
from shared.io_utils import load_json, save_json
from shared.models import DiscoveredItem, EnrichedItem
from shared.tmdb_client import TMDBClient

console = Console()

REFRESH_REPORT_FILE = f"{DATA_DIR}/7_refresh_report.json"

METADATA_FIELDS = [
    "id",
    "mediaType",
    "title",
    "synopsis",
    "coverImage",
    "cast",
    "platforms",
    "releaseYear",
    "runtime",
]


def normalize_title(title: str) -> str:
    return "".join(char for char in (title or "").casefold() if char.isalnum())


def discovered_from_show(show: Dict[str, Any], media_type: str) -> DiscoveredItem:
    return DiscoveredItem(
        tmdb_id=int(show["tmdbId"]),
        media_type=media_type,
        title=show.get("title", ""),
        original_title=show.get("title", ""),
        overview=show.get("synopsis", ""),
        poster_path=None,
        release_date=None,
        vote_average=0.0,
        vote_count=0,
        popularity=0.0,
        genre_ids=[],
    )


def show_from_enriched(existing: Dict[str, Any], enriched: EnrichedItem) -> Dict[str, Any]:
    updated = dict(existing)
    updated.update(
        {
            "id": enriched.imdb_id or existing.get("id"),
            "tmdbId": str(enriched.tmdb_id),
            "mediaType": enriched.media_type,
            "title": enriched.title,
            "synopsis": enriched.synopsis,
            "coverImage": enriched.cover_image_url,
            "cast": enriched.cast,
            "platforms": enriched.platforms,
            "releaseYear": enriched.release_year,
            "runtime": enriched.runtime,
        }
    )
    return updated


def diff_fields(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    changes = {}
    for field in METADATA_FIELDS:
        if before.get(field) != after.get(field):
            changes[field] = {
                "before": before.get(field),
                "after": after.get(field),
            }
    return changes


def fetch_best_match(
    client: TMDBClient,
    show: Dict[str, Any],
) -> Tuple[Optional[EnrichedItem], Optional[str]]:
    media_type = show.get("mediaType")
    candidates = [media_type] if media_type in {"tv", "movie"} else ["tv", "movie"]
    errors = []

    for candidate in candidates:
        try:
            enriched = enrich_from_tmdb(client, discovered_from_show(show, candidate))
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
            continue

        if not enriched:
            continue

        existing_imdb = show.get("id")
        if existing_imdb and enriched.imdb_id == existing_imdb:
            return enriched, None

        if media_type:
            return enriched, None

        if normalize_title(enriched.title) == normalize_title(show.get("title", "")):
            return enriched, None

    if errors:
        return None, "; ".join(errors)
    return None, "No TMDB match found"


def build_report(shows: List[Dict[str, Any]], limit: int = 0) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if not TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY not found in .env")

    client = TMDBClient(TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE)
    indexed = [
        (index, show)
        for index, show in enumerate(shows)
        if show.get("tmdbId") and str(show.get("tmdbId")).isdigit()
    ]
    if limit > 0:
        indexed = indexed[:limit]

    updates = []
    failures = []

    for index, show in track(indexed, description="Refreshing existing TMDB records"):
        enriched, error = fetch_best_match(client, show)
        if error:
            failures.append(
                {
                    "index": index,
                    "title": show.get("title"),
                    "tmdbId": show.get("tmdbId"),
                    "error": error,
                }
            )
            continue

        if not enriched:
            continue

        updated = show_from_enriched(show, enriched)
        changes = diff_fields(show, updated)
        if changes:
            updates.append(
                {
                    "index": index,
                    "title": show.get("title"),
                    "tmdbId": show.get("tmdbId"),
                    "mediaType": enriched.media_type,
                    "changes": changes,
                    "updated": updated,
                }
            )

    return updates, failures


def apply_updates(shows: List[Dict[str, Any]], updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    refreshed = list(shows)
    for update in updates:
        refreshed[update["index"]] = update["updated"]
    return refreshed


def print_summary(updates: List[Dict[str, Any]], failures: List[Dict[str, Any]], applied: bool) -> None:
    table = Table(title=f"Refresh Summary ({len(updates)} updates, {len(failures)} failures)")
    table.add_column("Title", style="cyan")
    table.add_column("TMDB", style="green")
    table.add_column("Fields", style="yellow")
    table.add_column("Action", style="magenta")

    for update in updates[:12]:
        table.add_row(
            update["title"] or "",
            str(update["tmdbId"]),
            ", ".join(update["changes"].keys()),
            "Applied" if applied else "Report only",
        )

    if len(updates) > 12:
        table.add_row("...", "...", "...", "...")

    console.print(table)
    if failures:
        console.print(f"[yellow]{len(failures)} records could not be refreshed. See {REFRESH_REPORT_FILE}.[/]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh existing shows.json metadata from TMDB.")
    parser.add_argument("--apply", action="store_true", help="Write metadata updates to shows.json.")
    parser.add_argument("--limit", type=int, default=0, help="Limit records for a test run.")
    args = parser.parse_args()

    shows = load_json(SHOWS_FILE) or []
    updates, failures = build_report(shows, args.limit)

    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "applied": args.apply,
        "updateCount": len(updates),
        "failureCount": len(failures),
        "updates": updates,
        "failures": failures,
    }
    save_json(REFRESH_REPORT_FILE, report)

    if args.apply and updates:
        save_json(SHOWS_FILE, apply_updates(shows, updates))

    print_summary(updates, failures, args.apply)
    console.print(f"[green]Report saved to {REFRESH_REPORT_FILE}[/]")


if __name__ == "__main__":
    main()
