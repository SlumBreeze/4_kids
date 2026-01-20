from rich.console import Console
from rich.progress import track
from shared.tmdb_client import TMDBClient
from shared.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE, TV_DISCOVERY_FILTERS, MOVIE_DISCOVERY_FILTERS, DISCOVERED_FILE
from shared.io_utils import save_json
from shared.models import DiscoveredItem

console = Console()

def discover_content(
    client: TMDBClient,
    media_type: str,
    filters: dict,
    target_count: int,
    max_pages: int = 50
):
    """Discover content from TMDB"""
    items = []
    seen_ids = set()

    console.print(f"[cyan]Discovering {media_type}s...[/]")

    # Fetch first page to get total
    page1 = client.discover_tv(1, **filters) if media_type == 'tv' else client.discover_movies(1, **filters)
    total_pages = min(page1['total_pages'], max_pages)

    console.print(f"Found {page1['total_results']} results across {total_pages} pages")

    # Fetch pages until we hit target count or run out
    for page in track(range(1, total_pages + 1), description=f"Fetching pages"):
        data = client.discover_tv(page, **filters) if media_type == 'tv' else client.discover_movies(page, **filters)

        for result in data['results']:
            if result['id'] in seen_ids:
                continue
            seen_ids.add(result['id'])
            item = DiscoveredItem(
                tmdb_id=result['id'],
                media_type=media_type,
                title=result.get('name') or result.get('title'),
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

            if len(items) >= target_count:
                return items[:target_count]

    return items

def main():
    console.rule("[bold blue]Stage 1: TMDB Discovery[/]")

    if not TMDB_API_KEY:
        console.print("[red]TMDB_API_KEY not found in .env file. Please add it and try again.[/]")
        return

    client = TMDBClient(TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE)

    # Discover TV shows
    tv_items = discover_content(client, 'tv', TV_DISCOVERY_FILTERS, target_count=100)

    # Discover movies
    movie_items = discover_content(client, 'movie', MOVIE_DISCOVERY_FILTERS, target_count=30)

    # Combine and deduplicate
    all_items = tv_items + movie_items
    console.print(f"\n[green]Total discovered: {len(all_items)} items[/]")

    # Save to staging
    save_json(DISCOVERED_FILE, [item.to_dict() for item in all_items])
    console.print(f"[bold green]✓ Saved to {DISCOVERED_FILE}[/]")

if __name__ == "__main__":
    main()
