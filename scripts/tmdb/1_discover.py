import json
import os
from rich.console import Console
from rich.progress import track
from shared.tmdb_client import TMDBClient
from shared.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE, TV_DISCOVERY_FILTERS, MOVIE_DISCOVERY_FILTERS, DISCOVERED_FILE
from shared.io_utils import save_json
from shared.models import DiscoveredItem

console = Console()

# Path to existing data
SHOWS_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "data", "shows.json")

def load_existing_data():
    """Load existing shows to build exclusion and legacy sets"""
    if not os.path.exists(SHOWS_DATA_FILE):
        return set(), set()

    try:
        with open(SHOWS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        existing_tmdb_ids = set()
        legacy_titles = set()

        for item in data:
            # If it has a numeric tmdbId, it's fully managed
            if item.get('tmdbId'):
                existing_tmdb_ids.add(int(item['tmdbId']))
            # If it has no tmdbId but has value, it's legacy/manual -> we might want to "upgrade" it if we find it
            else:
                legacy_titles.add(item['title'].lower().strip())

        return existing_tmdb_ids, legacy_titles
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load existing data: {e}[/]")
        return set(), set()

def discover_content(
    client: TMDBClient,
    media_type: str,
    filters: dict,
    target_count: int,
    existing_ids: set,
    legacy_titles: set,
    max_pages: int = 100
):
    """Discover content from TMDB with smart deduplication"""
    items = []
    seen_ids_this_run = set()

    console.print(f"[cyan]Discovering {media_type}s...[/]")

    # We loop through pages until we hit target count
    current_page = 1
    total_new_found = 0

    # Progress bar wrapper
    with console.status(f"[bold green]Scanning pages for new content...[/]") as status:
        while current_page <= max_pages and total_new_found < target_count:
            try:
                # Fetch page
                data = client.discover_tv(current_page, **filters) if media_type == 'tv' else client.discover_movies(current_page, **filters)

                results = data.get('results', [])
                if not results:
                    break # No more results

                # Process results
                page_new_count = 0
                for result in results:
                    tmdb_id = result['id']

                    # 1. Skip if we just found it this run
                    if tmdb_id in seen_ids_this_run:
                        continue
                    seen_ids_this_run.add(tmdb_id)

                    # 2. Check overlap with existing DB
                    title = result.get('name') or result.get('title')
                    is_legacy_upgrade = title and title.lower().strip() in legacy_titles

                    # If we ALREADY have this TMDB ID, skip it... UNLESS we want to force update (not implemented yet)
                    if tmdb_id in existing_ids:
                        # console.print(f"  [dim]Skipping existing: {title}[/]")
                        continue

                    # If it's NEW or a LEGACY UPGRADE
                    if is_legacy_upgrade:
                        console.print(f"  [green]FOUND LEGACY UPGRADE CANDIDATE: {title}[/]")

                    # Add it
                    item = DiscoveredItem(
                        tmdb_id=tmdb_id,
                        media_type=media_type,
                        title=title,
                        original_title=result.get('original_name') or result.get('original_title'),
                        overview=result.get('overview', ''),
                        poster_path=result.get('poster_path'),
                        release_date=result.get('first_air_date') or result.get('release_date'),
                        vote_average=result.get('vote_average', 0.0),
                        vote_count=result.get('vote_count', 0),
                        popularity=result.get('popularity', 0.0),
                        genre_ids=result.get('genre_ids', [])
                    )
                    items.append(item)
                    page_new_count += 1
                    total_new_found += 1

                    if total_new_found >= target_count:
                        break

                status.update(f"Page {current_page}: Found {page_new_count} new items (Total New: {total_new_found}/{target_count})")
                current_page += 1

                if current_page > data['total_pages']:
                    break

            except Exception as e:
                console.print(f"[red]Error on page {current_page}: {e}[/]")
                break

    console.print(f"Finished discovery. Found {len(items)} new/upgradeable items across {current_page-1} pages.")
    return items

def main():
    console.rule("[bold blue]Stage 1: TMDB Discovery (Smart Mode)[/]")

    if not TMDB_API_KEY:
        console.print("[red]TMDB_API_KEY not found in .env file. Please add it and try again.[/]")
        return

    # Load context
    existing_ids, legacy_titles = load_existing_data()
    console.print(f"[dim]Loaded {len(existing_ids)} existing items and {len(legacy_titles)} legacy titles to check against.[/]")

    client = TMDBClient(TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE)

    # Discover TV shows
    # We increase target count because many will be skipped
    tv_items = discover_content(
        client, 'tv', TV_DISCOVERY_FILTERS,
        target_count=80,
        existing_ids=existing_ids,
        legacy_titles=legacy_titles
    )

    # Discover movies
    movie_items = discover_content(
        client, 'movie', MOVIE_DISCOVERY_FILTERS,
        target_count=20,
        existing_ids=existing_ids,
        legacy_titles=legacy_titles
    )

    # Combine and save
    all_items = tv_items + movie_items
    console.print(f"\n[green]Total NEW discovered: {len(all_items)} items[/]")

    # Save to staging
    save_json(DISCOVERED_FILE, [item.to_dict() for item in all_items])
    console.print(f"[bold green][OK] Saved to {DISCOVERED_FILE}[/]")

if __name__ == "__main__":
    main()
