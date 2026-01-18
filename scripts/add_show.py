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

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract JSON-LD
    json_ld_script = soup.find('script', {'type': 'application/ld+json'})

    description = ''
    image = ''
    cast = []
    duration = ''
    year_range = ''

    if json_ld_script:
        try:
            data = json.loads(json_ld_script.string)
            description = data.get('description', 'No description found.')
            image = data.get('image', '')
            cast = [actor['name'] for actor in data.get('actor', [])[:3]] if 'actor' in data else []
            duration = parse_duration(data.get('duration', ''))
        except:
            pass

    # Scrape year range from page title (e.g., "Bluey (TV Series 2018– )" or "The Owl House (TV Series 2020–2023)")
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        # Match patterns like "2018– )" or "2020–2023)"
        year_match = re.search(r'(\d{4})[–\-–]+(\d{4}|\s*\))', title_text)
        if year_match:
            start = year_match.group(1)
            end_part = year_match.group(2).strip()
            if ')' in end_part or end_part == '':
                year_range = f"{start}–Present"
            else:
                year_range = f"{start}–{end_part}"

    # Fallback: try to get runtime from technical specs if JSON-LD didn't have it
    if not duration:
        runtime_elem = soup.select_one('[data-testid="title-techspec_runtime"] .ipc-metadata-list-item__content-container')
        if runtime_elem:
            duration = runtime_elem.get_text().strip()

    return {
        'description': description,
        'image': image,
        'cast': cast,
        'duration': duration,
        'year_range': year_range
    }

def load_shows():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_shows(shows):
    with open(DATA_FILE, 'w') as f:
        json.dump(shows, f, indent=2)

def main():
    console.rule("[bold blue]KidShow Scout - Data Ingestion Tool[/]")

    while True:
        # 1. Search
        query = Prompt.ask("Search for a show")
        results = search_imdb(query)

        if not results:
            console.print("[red]No results found.[/]")
            if Confirm.ask("Search again?"):
                continue
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

        # Auto-scraped fields (no prompts needed)
        release_year = details.get('year_range', '') or str(selected.get('year', ''))
        runtime = details.get('duration', '')

        console.print(f"Auto-scraped Year: [bold cyan]{release_year}[/]")
        console.print(f"Auto-scraped Runtime: [bold cyan]{runtime if runtime else 'Not found'}[/]")

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

        # 4. Save (check for duplicates by ID or by title+year)
        shows = load_shows()

        # Check for existing entry by ID or by title+year
        existing_by_id = next((s for s in shows if s['id'] == new_show['id']), None)
        existing_by_title = next((s for s in shows if s['title'].lower() == new_show['title'].lower() and s.get('releaseYear', '').startswith(release_year[:4])), None)
        existing = existing_by_id or existing_by_title

        if existing:
            if Confirm.ask(f"[yellow]{new_show['title']} ({existing['id']}) already exists. Overwrite?[/]"):
                # Remove the old entry (by its actual ID)
                shows = [s for s in shows if s['id'] != existing['id']]
                shows.append(new_show)
        else:
            shows.append(new_show)

        save_shows(shows)
        console.print(f"[bold green]Successfully added {selected['title']}![/]")

        if not Confirm.ask("Add another show? (Ctrl+C to exit)"):
            return

if __name__ == "__main__":
    main()
