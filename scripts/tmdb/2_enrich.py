from rich.console import Console
from rich.progress import track
from typing import Optional
from shared.tmdb_client import TMDBClient
from shared.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE, DISCOVERED_FILE, ENRICHED_FILE
from shared.io_utils import load_json, save_json
from shared.models import DiscoveredItem, EnrichedItem
from shared.enrichment import enrich_from_tmdb

console = Console()

def enrich_item(client: TMDBClient, discovered: DiscoveredItem) -> Optional[EnrichedItem]:
    """Fetch full details for a discovered item"""
    try:
        enriched = enrich_from_tmdb(client, discovered)
        if not enriched:
            console.print(f"[yellow]Warning: No IMDb ID for {discovered.title} (skipping)[/]")
            return None
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

    # Load existing enriched items for resumability
    existing_enriched = load_json(ENRICHED_FILE) or []
    enriched_items = [EnrichedItem.from_dict(item) for item in existing_enriched]
    enriched_ids = {item.tmdb_id for item in enriched_items}

    remaining_items = [item for item in discovered_items if item.tmdb_id not in enriched_ids]

    if not remaining_items:
        console.print("[green]All discovered items already enriched. Nothing to do.[/]")
        return

    if len(enriched_items) > 0:
        console.print(f"[yellow]Resuming: {len(enriched_items)} already enriched, {len(remaining_items)} remaining.[/]\n")

    for index, item in enumerate(track(remaining_items, description="Fetching details"), start=1):
        enriched = enrich_item(client, item)
        if enriched:
            enriched_items.append(enriched)

        # Save progress periodically
        if index % 10 == 0:
            save_json(ENRICHED_FILE, [entry.to_dict() for entry in enriched_items])

    console.print(f"\n[green]Successfully enriched: {len(enriched_items)} total[/]")

    # Save to staging
    save_json(ENRICHED_FILE, [item.to_dict() for item in enriched_items])
    console.print(f"[bold green][OK] Saved to {ENRICHED_FILE}[/]")

if __name__ == "__main__":
    main()
