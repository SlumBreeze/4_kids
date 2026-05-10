from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Set

from rich.console import Console
from rich.table import Table

from shared.config import DATA_DIR, SHOWS_FILE
from shared.io_utils import load_json, save_json

console = Console()

VARIANT_REPORT_FILE = f"{DATA_DIR}/8_variant_audit.json"
STOP_WORDS = {
    "a",
    "and",
    "for",
    "in",
    "of",
    "on",
    "the",
    "to",
    "tv",
    "with",
}


def title_tokens(title: str) -> Set[str]:
    token = []
    tokens = set()
    for char in (title or "").casefold():
        if char.isalnum():
            token.append(char)
        elif token:
            word = "".join(token)
            if len(word) > 1 and word not in STOP_WORDS:
                tokens.add(word)
            token = []
    if token:
        word = "".join(token)
        if len(word) > 1 and word not in STOP_WORDS:
            tokens.add(word)
    return tokens


def normalized_title(title: str) -> str:
    return "".join(char for char in (title or "").casefold() if char.isalnum())


def find_duplicate_ids(shows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_key = defaultdict(list)
    for index, show in enumerate(shows):
        tmdb_id = show.get("tmdbId")
        media_type = show.get("mediaType", "unknown")
        imdb_id = show.get("id")
        if tmdb_id:
            by_key[f"tmdb:{media_type}:{tmdb_id}"].append((index, show))
        if imdb_id:
            by_key[f"imdb:{imdb_id}"].append((index, show))

    duplicates = []
    for key, matches in by_key.items():
        if len(matches) > 1:
            duplicates.append(
                {
                    "key": key,
                    "items": [
                        {
                            "index": index,
                            "title": show.get("title"),
                            "tmdbId": show.get("tmdbId"),
                            "mediaType": show.get("mediaType"),
                            "id": show.get("id"),
                        }
                        for index, show in matches
                    ],
                }
            )
    return duplicates


def find_title_variants(shows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    exact_groups = defaultdict(list)
    token_rows = []

    for index, show in enumerate(shows):
        title = show.get("title", "")
        exact_groups[normalized_title(title)].append((index, show))
        token_rows.append((index, show, title_tokens(title)))

    variants = []
    seen_pairs = set()

    for key, matches in exact_groups.items():
        if key and len(matches) > 1:
            variants.append(
                {
                    "reason": "same_normalized_title",
                    "items": [
                        {
                            "index": index,
                            "title": show.get("title"),
                            "tmdbId": show.get("tmdbId"),
                            "mediaType": show.get("mediaType"),
                        }
                        for index, show in matches
                    ],
                }
            )

    for left_index, left_show, left_tokens in token_rows:
        if len(left_tokens) < 2:
            continue
        for right_index, right_show, right_tokens in token_rows:
            if right_index <= left_index or len(right_tokens) < 2:
                continue
            shared = left_tokens & right_tokens
            shorter = min(len(left_tokens), len(right_tokens))
            if len(shared) >= 2 and len(shared) / shorter >= 0.67:
                pair_key = tuple(sorted([left_index, right_index]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                variants.append(
                    {
                        "reason": "high_title_overlap",
                        "sharedTokens": sorted(shared),
                        "items": [
                            {
                                "index": left_index,
                                "title": left_show.get("title"),
                                "tmdbId": left_show.get("tmdbId"),
                                "mediaType": left_show.get("mediaType"),
                            },
                            {
                                "index": right_index,
                                "title": right_show.get("title"),
                                "tmdbId": right_show.get("tmdbId"),
                                "mediaType": right_show.get("mediaType"),
                            },
                        ],
                    }
                )

    return variants


def print_summary(duplicates: List[Dict[str, Any]], variants: List[Dict[str, Any]]) -> None:
    table = Table(title=f"Variant Audit ({len(duplicates)} duplicate IDs, {len(variants)} possible variants)")
    table.add_column("Reason", style="yellow")
    table.add_column("Titles", style="cyan")

    for item in (duplicates + variants)[:12]:
        titles = " | ".join(entry.get("title") or "" for entry in item["items"])
        table.add_row(item.get("key") or item.get("reason", ""), titles)

    if len(duplicates) + len(variants) > 12:
        table.add_row("...", "...")

    console.print(table)
    console.print(f"[green]Report saved to {VARIANT_REPORT_FILE}[/]")


def main() -> None:
    shows = load_json(SHOWS_FILE) or []
    duplicates = find_duplicate_ids(shows)
    variants = find_title_variants(shows)
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "duplicateIds": duplicates,
        "possibleVariants": variants,
    }
    save_json(VARIANT_REPORT_FILE, report)
    print_summary(duplicates, variants)


if __name__ == "__main__":
    main()
