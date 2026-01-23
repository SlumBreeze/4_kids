from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from datetime import datetime
from typing import Optional
from shared.io_utils import load_json, save_json, format_age_label, parse_age_input
from shared.models import AssessedItem, ReviewedItem
from shared.config import ASSESSED_FILE, REVIEWED_FILE

console = Console()

def display_item_details(item: AssessedItem):
    """Display full item details in Rich panel"""

    ai = item.assessment
    enriched = item.enriched

    # Build tags from AI assessment
    suggested_tags = []
    if ai.is_educational:
        suggested_tags.append("Educational")
    if ai.has_lgbtq:
        suggested_tags.append("LGBTQ+ Themes")
    if ai.has_violence:
        suggested_tags.append("Violence")
    if ai.has_scary:
        suggested_tags.append("Scary Imagery")

    details = f"""
[bold cyan]Title:[/] {enriched.title} ({enriched.release_year})
[bold cyan]TMDB ID:[/] {enriched.tmdb_id} | [bold cyan]IMDb ID:[/] {enriched.imdb_id or 'N/A'}
[bold cyan]Runtime:[/] {enriched.runtime or 'N/A'} | [bold cyan]Cert:[/] {enriched.certification or 'N/A'}

[bold yellow]Synopsis:[/]
{enriched.synopsis[:300]}{'...' if len(enriched.synopsis) > 300 else ''}

[bold yellow]Cast:[/] {', '.join(enriched.cast[:3]) or 'N/A'}
[bold yellow]Genres:[/] {', '.join(enriched.genres)}
[bold yellow]Platforms:[/] {', '.join(enriched.platforms) or 'None found'}

[bold green]AI Assessment:[/]
  Rating: {ai.rating}
  Ages: {format_age_label(ai.min_age)} - {format_age_label(ai.max_age)}
  Stimulation: {ai.stimulation_level}
  Tags: {', '.join(suggested_tags) or 'None'}

[bold green]Reasoning:[/]
{ai.reasoning}
"""

    border_color = "green" if ai.rating == "Safe" else "yellow" if ai.rating == "Caution" else "red"
    console.print(Panel(details, title=f"Review Item {item.enriched.tmdb_id}", border_style=border_color))

def prompt_review_decision(item: AssessedItem) -> Optional[ReviewedItem]:
    """Interactive review workflow"""

    console.rule(f"[bold blue]Reviewing: {item.enriched.title}[/]")
    display_item_details(item)

    # Decision
    console.print("\n[bold]Actions:[/] [cyan](A)ccept[/] | [yellow](E)dit[/] | [red](R)eject[/] | [dim](S)kip for later[/]")
    action = Prompt.ask("Choose action", choices=["a", "e", "r", "s"], default="a").lower()

    if action == "r":
        console.print("[red]Rejected. Item will NOT be saved.[/]")
        return None

    if action == "s":
        console.print("[dim]Skipped. Item remains in queue.[/dim]")
        return "SKIP"  # Special marker

    # Accept or Edit
    ai = item.assessment

    if action == "a":
        # Accept AI suggestions as-is
        rating = ai.rating
        min_age = ai.min_age
        max_age = ai.max_age
        stim_level = ai.stimulation_level
        reasoning = ai.reasoning

        tags = []
        if ai.is_educational:
            tags.append("Educational")
        if ai.has_lgbtq:
            tags.append("LGBTQ+ Themes")
        if ai.has_violence:
            tags.append("Violence")
        if ai.has_scary:
            tags.append("Scary Imagery")

        featured = False

    else:  # Edit
        console.print("\n[bold yellow]Edit Mode - Press Enter to keep AI suggestion[/]")

        # Rating
        rating = Prompt.ask(
            f"Rating [dim](AI: {ai.rating})[/]",
            choices=["Safe", "Caution", "Unsafe"],
            default=ai.rating
        )

        # Tags
        tags = []
        console.print(f"\n[bold]Content Tags:[/] [dim](AI suggested: {', '.join([t for t in [ai.is_educational and 'Educational', ai.has_lgbtq and 'LGBTQ+', ai.has_violence and 'Violence', ai.has_scary and 'Scary'] if t])})[/dim]")
        if Confirm.ask("Educational?", default=ai.is_educational):
            tags.append("Educational")
        if Confirm.ask("LGBTQ+ Themes?", default=ai.has_lgbtq):
            tags.append("LGBTQ+ Themes")
        if Confirm.ask("Violence?", default=ai.has_violence):
            tags.append("Violence")
        if Confirm.ask("Scary Imagery?", default=ai.has_scary):
            tags.append("Scary Imagery")
        if Confirm.ask("Fantasy?", default=False):
            tags.append("Fantasy")
        if Confirm.ask("Action?", default=False):
            tags.append("Action")
        if Confirm.ask("Values: Friendship?", default=False):
            tags.append("Values: Friendship")
        if Confirm.ask("Values: Family?", default=False):
            tags.append("Values: Family")

        # Ages
        min_age = parse_age_input(
            f"Minimum Age [dim](AI: {format_age_label(ai.min_age)})[/]",
            default=str(ai.min_age)
        )
        max_age = parse_age_input(
            f"Maximum Age [dim](AI: {format_age_label(ai.max_age)})[/]",
            default=str(ai.max_age)
        )

        # Stimulation
        stim_level = Prompt.ask(
            f"Stimulation Level [dim](AI: {ai.stimulation_level})[/]",
            choices=["Low", "Medium", "High"],
            default=ai.stimulation_level
        )

        # Reasoning
        console.print(f"\n[bold]AI Reasoning:[/] [dim]{ai.reasoning}[/dim]")
        if Confirm.ask("Edit reasoning?", default=False):
            reasoning = Prompt.ask("Enter your reasoning")
        else:
            reasoning = ai.reasoning

        # Featured
        featured = Confirm.ask("Mark as featured?", default=False)

    # Build reviewed item
    reviewed = ReviewedItem(
        enriched=item.enriched,
        rating=rating,
        tags=tags,
        reasoning=reasoning,
        min_age=min_age,
        max_age=max_age,
        stimulation_level=stim_level,
        featured=featured,
        safe_above_age=item.assessment.safe_above_age,
        is_episodic_issue=item.assessment.is_episodic_issue,
        ai_suggestion=item.assessment,
        reviewed_at=datetime.utcnow().isoformat()
    )

    console.print(f"[bold green]✓ Approved: {item.enriched.title}[/]")
    return reviewed

def main():
    """Review queue main loop"""
    console.rule("[bold blue]TMDB Review Queue[/]")

    # Load assessed items
    assessed_data = load_json(ASSESSED_FILE)
    if not assessed_data:
        console.print("[yellow]No items to review. Run 3_assess.py first.[/]")
        return

    # Convert to AssessedItem objects
    items = [AssessedItem.from_dict(item) for item in assessed_data]

    # Load existing reviewed items
    reviewed_data = load_json(REVIEWED_FILE) or []
    reviewed_ids = {item['enriched']['tmdb_id'] for item in reviewed_data}

    # Filter out already reviewed
    pending = [item for item in items if item.enriched.tmdb_id not in reviewed_ids]

    if not pending:
        console.print("[green]All items already reviewed![/]")
        return

    console.print(f"[cyan]Found {len(pending)} items pending review[/]\n")

    # Review loop
    approved = []
    skipped = []

    for idx, item in enumerate(pending, 1):
        console.print(f"\n[bold]Progress: {idx}/{len(pending)}[/]")

        result = prompt_review_decision(item)

        if result == "SKIP":
            skipped.append(item)
        elif result is not None:
            approved.append(result)

        # Continue?
        if idx < len(pending):
            if not Confirm.ask("\nContinue to next item?", default=True):
                break

    # Save approved items
    if approved:
        # Append to existing reviewed.json
        for item in approved:
            reviewed_data.append(item.to_dict())

        save_json(REVIEWED_FILE, reviewed_data)
        console.print(f"\n[bold green]✓ Saved {len(approved)} approved items to {REVIEWED_FILE}[/]")

    # Summary
    console.rule("[bold green]Review Session Complete[/]")
    console.print(f"Approved: {len(approved)}")
    console.print(f"Rejected: {len(pending) - len(approved) - len(skipped)}")
    console.print(f"Skipped: {len(skipped)}")

if __name__ == "__main__":
    main()
