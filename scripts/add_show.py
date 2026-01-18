import requests
import json
import re
import os
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich import print

console = Console()

IMDB_SUGGEST_URL = "https://v3.sg.media-imdb.com/suggestion"
DATA_FILE = os.path.join(os.path.dirname(__file__), '../src/data/shows.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def search_imdb(query):
    first_letter = query[0].lower() if query else 'a'
    url = f"{IMDB_SUGGEST_URL}/{first_letter}/{query}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    results = []
    if 'd' in data:
        for item in data['d']:
            if item['id'].startswith('tt'): # Only titles
                results.append({
                    'id': item['id'],
                    'title': item['l'],
                    'year': item.get('y'),
                    'image': item.get('i', {}).get('imageUrl')
                })
    return results

def parse_duration(duration_str):
    if not duration_str:
        return ""
    # PT22M -> 22 min
    match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
    if match:
        h = match.group(1)
        m = match.group(2)
        parts = []
        if h: parts.append(f"{h} hr")
        if m: parts.append(f"{m} min")
        return " ".join(parts)
    return ""

def get_movie_details(imdb_id):
    url = f"https://www.imdb.com/title/{imdb_id}/"
    response = requests.get(url, headers=HEADERS)

    # Extract JSON-LD
    soup = BeautifulSoup(response.text, 'html.parser')
    json_ld_script = soup.find('script', {'type': 'application/ld+json'})

    if json_ld_script:
        try:
            data = json.loads(json_ld_script.string)
            duration_iso = data.get('duration', '')

            return {
                'description': data.get('description', 'No description found.'),
                'image': data.get('image', ''),
                'cast': [actor['name'] for actor in data.get('actor', [])[:3]] if 'actor' in data else [],
                'duration': parse_duration(duration_iso)
            }
        except:
            pass

    return {'description': '', 'image': '', 'cast': [], 'duration': ''}

def load_shows():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_shows(shows):
    with open(DATA_FILE, 'w') as f:
        json.dump(shows, f, indent=2)

def main():
    console.rule("[bold blue]KidShow Scout - Data Ingestion Tool[/]")

    # 1. Search
    query = Prompt.ask("Search for a show")
    results = search_imdb(query)

    if not results:
        console.print("[red]No results found.[/]")
        return

    table = Table(title="Search Results")
    table.add_column("Index", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Year", style="green")

    for idx, r in enumerate(results):
        table.add_row(str(idx + 1), r['title'], str(r['year']))

    console.print(table)

    selection_idx = IntPrompt.ask("Select a show by index", choices=[str(i+1) for i in range(len(results))])
    selected = results[selection_idx - 1]

    # 2. Fetch Details
    console.print(f"[yellow]Fetching details for {selected['title']}...[/]")
    details = get_movie_details(selected['id'])

    # 3. Interview Phase
    console.rule("[bold green]Safety Assessment[/]")

    tags = []
    has_lgbtq = Confirm.ask("Does this show have [bold red]LGBTQ+ Themes[/]?")
    if has_lgbtq: tags.append("LGBTQ+ Themes")

    has_violence = Confirm.ask("Does it contain [bold red]Violence[/]?")
    if has_violence: tags.append("Violence")

    if Confirm.ask("Is it [bold blue]Educational[/]?"): tags.append("Educational")
    if Confirm.ask("Is it a [bold magenta]Comedy[/]?"): tags.append("Comedy")

    # Smart Default for Rating
    # Auto-determine Rating
    rating = "Safe"
    if has_lgbtq:
        rating = "Unsafe"
    elif has_violence:
        rating = "Caution"
    console.print(f"Auto-assigned Rating: [bold cyan]{rating}[/]")

    reasoning = Prompt.ask("Enter reasoning/opinion (Why is it safe/unsafe?)")
    min_age = float(Prompt.ask("Minimum Age (e.g. 0.5, 3, 7)"))
    max_age = float(Prompt.ask("Maximum Age (e.g. 5, 12, 99)", default="99"))

    # Auto-scrape fields
    release_year = str(selected.get('year', ''))
    runtime = details.get('duration', '')

    console.print(f"Auto-scraped Year: [bold cyan]{release_year}[/]")
    console.print(f"Auto-scraped Runtime: [bold cyan]{runtime}[/]")

    stim_level = Prompt.ask("Stimulation Level", choices=["Low", "Medium", "High"], default="Medium")

    stim_level = Prompt.ask("Stimulation Level", choices=["Low", "Medium", "High"], default="Medium")

    new_show = {
        "id": selected['id'],
        "title": selected['title'],
        "synopsis": details['description'],
        "coverImage": details['image'] if details['image'] else selected['image'],
        "cast": details['cast'],
        "tags": tags,
        "rating": rating,
        "reasoning": reasoning,
        "ageRecommendation": f"{int(min_age)}+" if max_age == 99 else f"{min_age}-{max_age}",
        "minAge": min_age,
        "maxAge": max_age,
        "releaseYear": release_year,
        "runtime": runtime,
        "stimulationLevel": stim_level
    }

    # 4. Save
    shows = load_shows()
    if any(s['id'] == new_show['id'] for s in shows):
        if Confirm.ask(f"[yellow]{selected['title']} already exists. Overwrite?[/]"):
            shows = [s for s in shows if s['id'] != new_show['id']]
            shows.append(new_show)
    else:
        shows.append(new_show)

    save_shows(shows)
    console.print(f"[bold green]Successfully added {selected['title']}![/]")

if __name__ == "__main__":
    main()
