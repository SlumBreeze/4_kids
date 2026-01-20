from rich.console import Console
from rich.progress import track
from typing import Optional
from shared.tmdb_client import TMDBClient
from shared.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE, DISCOVERED_FILE, ENRICHED_FILE
from shared.io_utils import load_json, save_json
from shared.models import DiscoveredItem, EnrichedItem

console = Console()

def enrich_item(client: TMDBClient, discovered: DiscoveredItem) -> Optional[EnrichedItem]:
    """Fetch full details for a discovered item"""
    try:
        # Fetch full details
        if discovered.media_type == 'tv':
            details = client.get_tv_details(discovered.tmdb_id)
        else:
            details = client.get_movie_details(discovered.tmdb_id)

        # Extract IMDb ID
        external_ids = details.get('external_ids', {})
        imdb_id = external_ids.get('imdb_id')

        if not imdb_id:
            console.print(f"[yellow]Warning: No IMDb ID for {discovered.title} (skipping)[/]")
            return None

        # Extract cast (top 3)
        credits = details.get('credits', {})
        cast = [actor['name'] for actor in credits.get('cast', [])[:3]]

        # Extract genres
        genres = [g['name'] for g in details.get('genres', [])]

        # Extract platforms
        providers = details.get('watch/providers', {})
        platforms = client.extract_platforms(providers)

        # Extract certification
        if discovered.media_type == 'tv':
            cert = client.extract_certification(details.get('content_ratings', {}), 'tv')
        else:
            cert = client.extract_certification(details.get('release_dates', {}), 'movie')

        # Extract runtime
        runtime_str = ""
        if discovered.media_type == 'tv':
            episode_runtimes = details.get('episode_run_time', [])
            if episode_runtimes:
                runtime_str = client.format_runtime(episode_runtimes[0])
        else:
            runtime_str = client.format_runtime(details.get('runtime'))

        # Build enriched item
        enriched = EnrichedItem(
            tmdb_id=discovered.tmdb_id,
            media_type=discovered.media_type,
            title=discovered.title,
            synopsis=details.get('overview', discovered.overview),
            cover_image_url=client.get_image_url(details.get('poster_path')),
            imdb_id=imdb_id,
            release_year=client.format_year_range(details, discovered.media_type),
            runtime=runtime_str,
            cast=cast,
            genres=genres,
            certification=cert,
            platforms=platforms,
            popularity=discovered.popularity,
            vote_average=discovered.vote_average
        )

        return enriched

    except Exception as e:
        console.print(f"[red]Error enriching {discovered.title}: {e}[/]")
        return None

def main():
    console.rule("[bold blue]Stage 2: TMDB Enrichment[/]")

    # Load discovered items
    discovered_data = load_json(DISCOVERED_FILE)
    if not discovered_data:
        console.print("[red]No discovered items found. Run 1_discover.py first.[/]")
        return

    discovered_items = [DiscoveredItem.from_dict(item) for item in discovered_data]
    console.print(f"[cyan]Enriching {len(discovered_items)} items...[/]\n")

    if not TMDB_API_KEY:
        console.print("[red]TMDB_API_KEY not found in .env file. Please add it and try again.[/]")
        return

    client = TMDBClient(TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE)
    enriched_items = []

    for item in track(discovered_items, description="Fetching details"):
        enriched = enrich_item(client, item)
        if enriched:
            enriched_items.append(enriched)

    console.print(f"\n[green]Successfully enriched: {len(enriched_items)}/{len(discovered_items)}[/]")

    # Save to staging
    save_json(ENRICHED_FILE, [item.to_dict() for item in enriched_items])
    console.print(f"[bold green]✓ Saved to {ENRICHED_FILE}[/]")

if __name__ == "__main__":
    main()
