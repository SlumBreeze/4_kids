import argparse
try:
    from rich.console import Console
    from rich.progress import track
except ModuleNotFoundError:
    Console = None

    def track(iterable, description=""):
        if description:
            print(description)
        return iterable

from shared.config import ENRICHED_FILE, ASSESSED_FILE
from shared.io_utils import load_json, save_json
from shared.models import EnrichedItem, AssessedItem
from shared.rule_assessor import assess_with_rules

console = Console() if Console else None
SAVE_EVERY = 50


def item_key(enriched: EnrichedItem) -> str:
    """Stable key for resume logic."""
    if enriched.imdb_id:
        return enriched.imdb_id
    return f"{enriched.media_type}:{enriched.tmdb_id}"


def assess_item(enriched: EnrichedItem) -> AssessedItem:
    assessment = assess_with_rules(enriched)
    return AssessedItem(
        enriched=enriched,
        assessment=assessment,
        flagged_for_review=assessment.needs_review(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Rule-based child-safety assessment.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Keep existing assessed records and only process missing enriched items.",
    )
    args = parser.parse_args()

    if console:
        console.rule("[bold blue]Stage 3: Rule-Based Safety Assessment[/]")
    else:
        print("Stage 3: Rule-Based Safety Assessment")

    enriched_data = load_json(ENRICHED_FILE)
    if not enriched_data:
        print("No enriched items found. Run 2_enrich.py first.")
        return

    enriched_items = [EnrichedItem.from_dict(item) for item in enriched_data]
    message = f"Assessing {len(enriched_items)} items with deterministic rules..."
    console.print(f"[cyan]{message}[/]\n") if console else print(message)

    if args.resume:
        existing_assessed = load_json(ASSESSED_FILE) or []
        assessed_items = [AssessedItem.from_dict(item) for item in existing_assessed]
        assessed_by_key = {item_key(item.enriched): item for item in assessed_items}
        remaining_items = [item for item in enriched_items if item_key(item) not in assessed_by_key]
        message = f"Resuming: {len(assessed_items)} already assessed, {len(remaining_items)} remaining."
        console.print(f"[cyan]{message}[/]\n") if console else print(message)
    else:
        assessed_items = []
        assessed_by_key = {}
        remaining_items = enriched_items
        message = "Rebuilding assessed staging from rules. Existing AI assessments will be overwritten."
        console.print(f"[yellow]{message}[/]\n") if console else print(message)

    flagged_count = sum(1 for item in assessed_items if item.flagged_for_review)

    for index, item in enumerate(track(remaining_items, description="Rule assessment"), start=1):
        assessed = assess_item(item)
        assessed_items.append(assessed)
        assessed_by_key[item_key(item)] = assessed
        if assessed.flagged_for_review:
            flagged_count += 1

        if index % SAVE_EVERY == 0:
            save_json(ASSESSED_FILE, [entry.to_dict() for entry in assessed_items])

    save_json(ASSESSED_FILE, [item.to_dict() for item in assessed_items])
    print(f"Successfully assessed: {len(assessed_items)}/{len(enriched_items)}")
    print(f"Flagged for review: {flagged_count}")
    print(f"Saved to {ASSESSED_FILE}")


if __name__ == "__main__":
    main()
