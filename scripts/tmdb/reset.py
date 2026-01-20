from rich.console import Console
from rich.prompt import Confirm
from shared.config import DATA_DIR, DISCOVERED_FILE, ENRICHED_FILE, ASSESSED_FILE, REVIEWED_FILE
import os

console = Console()

def main():
    console.rule("[bold red]TMDB Pipeline Reset[/]")
    console.print(f"[yellow]This will delete staged files in {DATA_DIR}[/]\n")

    if not Confirm.ask("Delete stage files?", default=False):
        console.print("[green]Reset cancelled[/]")
        return

    files = [DISCOVERED_FILE, ENRICHED_FILE, ASSESSED_FILE, REVIEWED_FILE]
    removed = 0

    for path in files:
        if os.path.exists(path):
            os.remove(path)
            removed += 1

    console.print(f"[bold green]✓ Removed {removed} file(s)[/]")

if __name__ == "__main__":
    main()
