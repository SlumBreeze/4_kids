"""
Stage 6: Re-assess existing shows.json entries

Only re-assesses shows that:
1. Have Violence or Scary Imagery tags (need safeAboveAge)
2. Don't have safeAboveAge set yet
3. Have rating of Caution or Unsafe (may benefit from age-aware logic)

Updates shows.json in place, preserving all other fields.
"""
import json
from datetime import datetime
from rich.console import Console
from rich.progress import track
from rich.prompt import Confirm
from shared.gemini_client import GeminiClient
from shared.config import GEMINI_API_KEY, SHOWS_FILE

console = Console()

def needs_reassessment(show: dict) -> bool:
    """Determine if a show needs re-assessment."""
    tags = show.get('tags', [])
    has_concerning_tags = 'Violence' in tags or 'Scary Imagery' in tags
    missing_safe_above = show.get('safeAboveAge') is None
    is_caution = show.get('rating') == 'Caution'
    is_unsafe = show.get('rating') == 'Unsafe'

    # Re-assess if:
    # 1. Currently Unsafe (Targeting episodic false positives per user request)
    return is_unsafe

def reassess_show(client: GeminiClient, show: dict) -> dict:
    """Re-assess a single show and update its fields."""
    try:
        # Build genres from tags (approximate)
        genres = []
        if 'Educational' in show.get('tags', []):
            genres.append('Family')
        if 'Fantasy' in show.get('tags', []):
            genres.append('Fantasy')
        if 'Action' in show.get('tags', []):
            genres.append('Action')

        assessment = client.assess_content_safety(
            title=show['title'],
            year=show.get('releaseYear', ''),
            synopsis=show.get('synopsis', ''),
            genres=genres,
            certification=None
        )

        if not assessment:
            console.print(f"[yellow]Warning: No assessment for {show['title']}[/]")
            return show

        # Update only the relevant fields, preserve everything else
        updated = show.copy()
        updated['safeAboveAge'] = assessment.get('safe_above_age')
        updated['isEpisodicIssue'] = assessment.get('is_episodic_issue', False)

        # Optionally update rating based on new assessment if it makes sense
        new_rating = assessment.get('rating', show['rating'])
        if new_rating != show['rating']:
            console.print(f"  [dim]{show['title']}: {show['rating']} → {new_rating}[/]")
        updated['rating'] = new_rating
        updated['reasoning'] = assessment.get('reasoning', show.get('reasoning', ''))

        return updated

    except Exception as e:
        console.print(f"[red]Error reassessing {show['title']}: {e}[/]")
        return show

def main():
    console.rule("[bold blue]Stage 6: Re-assess Existing Shows[/]")

    if not GEMINI_API_KEY:
        console.print("[red]GEMINI_API_KEY not found in .env file.[/]")
        return

    # Load shows.json
    try:
        with open(SHOWS_FILE, 'r', encoding='utf-8') as f:
            shows = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Shows file not found: {SHOWS_FILE}[/]")
        return

    console.print(f"[cyan]Loaded {len(shows)} shows from shows.json[/]")

    # Find shows needing re-assessment
    to_reassess = [s for s in shows if needs_reassessment(s)]

    if not to_reassess:
        console.print("[green]No shows need re-assessment![/]")
        return

    console.print(f"[yellow]Found {len(to_reassess)} shows needing re-assessment:[/]")
    for show in to_reassess[:10]:
        console.print(f"  - {show['title']} ({show.get('rating', 'N/A')})")
    if len(to_reassess) > 10:
        console.print(f"  ... and {len(to_reassess) - 10} more")

    if not Confirm.ask("\nProceed with re-assessment?", default=True):
        console.print("[dim]Cancelled.[/]")
        return

    # Initialize client and process
    client = GeminiClient(GEMINI_API_KEY)

    # Build lookup for quick updates
    shows_by_id = {s.get('id') or s.get('tmdbId'): s for s in shows}

    updated_count = 0
    for show in track(to_reassess, description="Re-assessing"):
        show_key = show.get('id') or show.get('tmdbId')
        updated_show = reassess_show(client, show)
        shows_by_id[show_key] = updated_show
        updated_count += 1

    # Rebuild list preserving order
    updated_shows = []
    seen_keys = set()
    for show in shows:
        key = show.get('id') or show.get('tmdbId')
        if key not in seen_keys:
            updated_shows.append(shows_by_id.get(key, show))
            seen_keys.add(key)

    # Backup and save
    backup_file = SHOWS_FILE.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(shows, f, indent=2, ensure_ascii=False)
    console.print(f"[dim]Backup saved to {backup_file}[/]")

    with open(SHOWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_shows, f, indent=2, ensure_ascii=False)

    console.print(f"\n[bold green]✓ Re-assessed {updated_count} shows[/]")
    console.print(f"[bold green]✓ Updated {SHOWS_FILE}[/]")

if __name__ == "__main__":
    main()
