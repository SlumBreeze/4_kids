from rich.console import Console
from rich.progress import track
from typing import Optional
from shared.gemini_client import GeminiClient
from shared.config import GEMINI_API_KEY, ENRICHED_FILE, ASSESSED_FILE
from shared.io_utils import load_json, save_json
from shared.models import EnrichedItem, AIAssessment, AssessedItem

console = Console()
SAVE_EVERY = 1
BATCH_LIMIT = 500 # Max items to process in one run (set to 0 for unlimited)

def item_key(enriched: EnrichedItem) -> str:
    """Stable key for resume logic."""
    if enriched.imdb_id:
        return enriched.imdb_id
    return f"{enriched.media_type}:{enriched.tmdb_id}"

def assess_item(client: GeminiClient, enriched: EnrichedItem) -> Optional[AssessedItem]:
    """Request AI safety assessment"""
    try:
        assessment_data = client.assess_content_safety(
            title=enriched.title,
            year=enriched.release_year or "",
            synopsis=enriched.synopsis,
            genres=enriched.genres,
            certification=enriched.certification
        )

        if not assessment_data:
            return None

        assessment = AIAssessment(
            rating=assessment_data.get('rating', 'Caution'),
            min_age=float(assessment_data.get('min_age', 3)),
            max_age=float(assessment_data.get('max_age', 99)),
            stimulation_level=assessment_data.get('stimulation_level', 'Medium'),
            has_lgbtq=bool(assessment_data.get('has_lgbtq', False)),
            has_violence=bool(assessment_data.get('has_violence', False)),
            has_scary=bool(assessment_data.get('has_scary', False)),
            is_educational=bool(assessment_data.get('is_educational', False)),
            reasoning=assessment_data.get('reasoning', '')
        )

        assessed = AssessedItem(
            enriched=enriched,
            assessment=assessment,
            flagged_for_review=assessment.needs_review()
        )

        return assessed

    except Exception as e:
        console.print(f"[red]Error assessing {enriched.title}: {e}[/]")
        return None

def main():
    console.rule("[bold blue]Stage 3: AI Safety Assessment[/]")

    # Load enriched items
    enriched_data = load_json(ENRICHED_FILE)
    if not enriched_data:
        console.print("[red]No enriched items found. Run 2_enrich.py first.[/]")
        return

    enriched_items = [EnrichedItem.from_dict(item) for item in enriched_data]
    console.print(f"[cyan]Assessing {len(enriched_items)} items with Gemini AI...[/]\n")

    if not GEMINI_API_KEY:
        console.print("[red]GEMINI_API_KEY not found in .env file. Please add it and try again.[/]")
        return

    client = GeminiClient(GEMINI_API_KEY)

    existing_assessed = load_json(ASSESSED_FILE) or []
    assessed_items = [AssessedItem.from_dict(item) for item in existing_assessed]
    assessed_by_key = {item_key(item.enriched): item for item in assessed_items}
    flagged_count = sum(1 for item in assessed_items if item.flagged_for_review)

    remaining_items = [item for item in enriched_items if item_key(item) not in assessed_by_key]

    if not remaining_items:
        console.print("[green]All items already assessed. Nothing to do.[/]")
        return

    # Apply batch limit
    if BATCH_LIMIT > 0 and len(remaining_items) > BATCH_LIMIT:
        console.print(f"[yellow]Batch limit active: Processing {BATCH_LIMIT} of {len(remaining_items)} remaining items.[/]")
        remaining_items = remaining_items[:BATCH_LIMIT]
    else:
        console.print(f"[cyan]Resuming: {len(assessed_items)} already assessed, {len(remaining_items)} remaining.[/]\n")

    for index, item in enumerate(track(remaining_items, description="AI Assessment"), start=1):
        assessed = assess_item(client, item)
        if assessed:
            assessed_items.append(assessed)
            assessed_by_key[item_key(item)] = assessed
            if assessed.flagged_for_review:
                flagged_count += 1

        if index % SAVE_EVERY == 0:
            save_json(ASSESSED_FILE, [entry.to_dict() for entry in assessed_items])

    console.print(f"\n[green]Successfully assessed: {len(assessed_items)}/{len(enriched_items)}[/]")
    console.print(f"[yellow]Flagged for review: {flagged_count}[/]")

    # Save to staging
    save_json(ASSESSED_FILE, [item.to_dict() for item in assessed_items])
    console.print(f"[bold green]✓ Saved to {ASSESSED_FILE}[/]")

if __name__ == "__main__":
    main()
