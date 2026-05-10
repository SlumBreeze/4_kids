import argparse
from datetime import datetime, timezone
from typing import Any, Dict, List

from rich.console import Console
from rich.progress import track
from rich.table import Table

from shared.config import DATA_DIR, SHOWS_FILE
from shared.io_utils import load_json, save_json
from shared.source_adapters import TVMazeAdapter, WikidataAdapter

console = Console()
FREE_SOURCE_REPORT_FILE = f"{DATA_DIR}/9_free_source_report.json"


def needs_fallback(show: Dict[str, Any]) -> bool:
    return any(
        not show.get(field)
        for field in ["id", "synopsis", "coverImage", "runtime", "releaseYear"]
    )


def build_report(shows: List[Dict[str, Any]], limit: int = 0) -> List[Dict[str, Any]]:
    tvmaze = TVMazeAdapter()
    wikidata = WikidataAdapter()
    candidates = [show for show in shows if needs_fallback(show)]
    if limit > 0:
        candidates = candidates[:limit]

    report_rows = []
    for show in track(candidates, description="Checking free fallback sources"):
        suggestions = []

        try:
            tvmaze_suggestion = tvmaze.lookup(show.get("title", ""))
            if tvmaze_suggestion:
                suggestions.append(tvmaze_suggestion.to_dict())
        except Exception as exc:
            suggestions.append({"source": "tvmaze", "error": str(exc)})

        try:
            wikidata_suggestion = wikidata.lookup_by_imdb(show.get("id", ""))
            if wikidata_suggestion:
                suggestions.append(wikidata_suggestion.to_dict())
        except Exception as exc:
            suggestions.append({"source": "wikidata", "error": str(exc)})

        if suggestions:
            report_rows.append(
                {
                    "title": show.get("title"),
                    "id": show.get("id"),
                    "tmdbId": show.get("tmdbId"),
                    "missingFields": [
                        field
                        for field in ["id", "synopsis", "coverImage", "runtime", "releaseYear"]
                        if not show.get(field)
                    ],
                    "suggestions": suggestions,
                }
            )

    return report_rows


def print_summary(rows: List[Dict[str, Any]]) -> None:
    table = Table(title=f"Free Source Report ({len(rows)} records)")
    table.add_column("Title", style="cyan")
    table.add_column("Missing", style="yellow")
    table.add_column("Sources", style="green")

    for row in rows[:12]:
        table.add_row(
            row.get("title") or "",
            ", ".join(row.get("missingFields") or []),
            ", ".join(suggestion.get("source", "") for suggestion in row.get("suggestions", [])),
        )

    if len(rows) > 12:
        table.add_row("...", "...", "...")

    console.print(table)
    console.print(f"[green]Report saved to {FREE_SOURCE_REPORT_FILE}[/]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check TVmaze and Wikidata for missing metadata suggestions.")
    parser.add_argument("--limit", type=int, default=0, help="Limit records for a test run.")
    args = parser.parse_args()

    shows = load_json(SHOWS_FILE) or []
    rows = build_report(shows, args.limit)
    save_json(
        FREE_SOURCE_REPORT_FILE,
        {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "recordCount": len(rows),
            "records": rows,
        },
    )
    print_summary(rows)


if __name__ == "__main__":
    main()
