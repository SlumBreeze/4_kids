import re
import argparse
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from shared.config import REVIEWED_FILE, SHOWS_FILE
from shared.io_utils import load_json, save_json
from shared.models import ReviewedItem

console = Console()

def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (title or "").casefold())

def main():
    parser = argparse.ArgumentParser(description="Import reviewed items into shows.json.")
    parser.add_argument(
        "--match-title",
        action="store_true",
        help="Allow replacing by normalized title when no ID match exists. Disabled by default to preserve variants.",
    )
    parser.add_argument("--yes", action="store_true", help="Accept import prompts with defaults.")
    args = parser.parse_args()

    console.rule("[bold blue]Stage 5: Import to shows.json[/]")

    # Load reviewed items
    reviewed_data = load_json(REVIEWED_FILE)
    if not reviewed_data:
        console.print("[red]No reviewed items found. Run 4_review.py first.[/]")
        return

    reviewed_items = [ReviewedItem.from_dict(item) for item in reviewed_data]
    console.print(f"[cyan]Found {len(reviewed_items)} reviewed items[/]\n")

    # Load existing shows
    shows = load_json(SHOWS_FILE) or []
    existing_by_id = {}
    existing_by_tmdb = {}
    existing_by_title = {}

    for index, show in enumerate(shows):
        show_id = show.get("id")
        if show_id:
            existing_by_id[show_id] = index

        tmdb_id = show.get("tmdbId")
        media_type = show.get("mediaType")
        if tmdb_id and media_type:
            existing_by_tmdb[(str(tmdb_id), media_type)] = index

        title_key = normalize_title(show.get("title", ""))
        if title_key:
            existing_by_title.setdefault(title_key, []).append(index)

    overwrite_existing = True if args.yes else Confirm.ask(
        "Overwrite existing shows when a match is found?",
        default=True
    )

    preview_rows = []
    add_count = 0
    replace_count = 0
    skip_count = 0

    for item in reviewed_items:
        show_data = item.to_show_format()
        match_index = None
        action = "Add"

        if show_data.get("minAge", 0) >= 6:
            action = "Skip (out of age scope)"
        elif show_data.get("maxAge", 0) > 5:
            action = "Skip (out of age scope)"

        tmdb_key = (str(show_data.get("tmdbId")), show_data.get("mediaType"))
        if action.startswith("Skip"):
            pass
        elif tmdb_key in existing_by_tmdb:
            match_index = existing_by_tmdb[tmdb_key]
        elif show_data.get("id") and show_data["id"] in existing_by_id:
            match_index = existing_by_id[show_data["id"]]
        elif args.match_title:
            title_key = normalize_title(show_data.get("title", ""))
            if title_key in existing_by_title and len(existing_by_title[title_key]) == 1:
                match_index = existing_by_title[title_key][0]
            elif title_key in existing_by_title and len(existing_by_title[title_key]) > 1:
                action = "Skip (ambiguous title)"

        if match_index is not None:
            if overwrite_existing:
                action = "Replace"
                replace_count += 1
            else:
                action = "Skip"
                skip_count += 1
        elif action.startswith("Skip"):
            skip_count += 1
        else:
            add_count += 1

        preview_rows.append((show_data, action, match_index))

    if add_count == 0 and replace_count == 0:
        console.print("[yellow]No items to import (all would be skipped)[/]")
        return

    # Display summary
    table = Table(title=f"Import Preview ({add_count} add, {replace_count} replace, {skip_count} skip)")
    table.add_column("Title", style="cyan")
    table.add_column("Rating", style="yellow")
    table.add_column("Ages", style="green")
    table.add_column("Action", style="magenta")

    for show_data, action, _ in preview_rows[:10]:  # Preview first 10
        table.add_row(
            show_data["title"],
            show_data["rating"],
            f"{show_data['minAge']}-{show_data['maxAge']}",
            action
        )

    if len(preview_rows) > 10:
        table.add_row("...", "...", "...", "...")

    console.print(table)

    # Confirm import
    if not args.yes and not Confirm.ask(
        f"\nImport {add_count} new and {replace_count} replacements to shows.json?",
        default=True
    ):
        console.print("[yellow]Import cancelled[/]")
        return

    # Apply changes
    for show_data, action, match_index in preview_rows:
        if action == "Replace" and match_index is not None:
            shows[match_index] = show_data
        elif action == "Add":
            shows.append(show_data)

    # Save
    save_json(SHOWS_FILE, shows)
    console.print(f"[bold green][OK] Successfully imported {add_count} shows and replaced {replace_count} shows in {SHOWS_FILE}[/]")
    console.print(f"[green]Total shows in database: {len(shows)}[/]")

if __name__ == "__main__":
    main()
