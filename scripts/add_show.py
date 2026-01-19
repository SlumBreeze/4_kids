import json
import os
import re
import requests
import sys
from urllib.parse import quote

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console = Console()

IMDB_SUGGEST_URL = "https://v3.sg.media-imdb.com/suggestion"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(ROOT_DIR, "src", "data", "shows.json")
ENV_FILE = os.path.join(ROOT_DIR, ".env")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

load_dotenv(ENV_FILE)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

def search_imdb(query):
    safe_query = query.strip()
    first_letter = safe_query[0].lower() if safe_query else "a"
    url = f"{IMDB_SUGGEST_URL}/{first_letter}/{quote(safe_query)}.json"
    response = requests.get(url, headers=HEADERS, timeout=10)
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
    response = requests.get(url, headers=HEADERS, timeout=10)

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

def normalize_age_value(value):
    try:
        age = float(value)
    except (TypeError, ValueError):
        return 0.0
    if age < 0:
        return 0.0
    if age < 1:
        # Interpret decimal as months in tenths: 0.4 -> 4 months, 0.5 -> 5 months.
        months = int(round(age * 10))
        return months / 10
    return age

def parse_age_input(label, default=None):
    default_text = None if default is None else str(default)
    raw = Prompt.ask(label, default=default_text)
    value = raw.strip().lower()
    if value.endswith(("mo", "mos", "m")):
        num = value.rstrip("mos").rstrip("m").strip()
        try:
            months = float(num)
        except ValueError:
            months = 0.0
        if months < 12:
            return max(0.0, round(months / 10, 1))
        return max(0.0, round(months / 12, 1))
    try:
        return normalize_age_value(float(value))
    except ValueError:
        return 0.0

def format_age_label(age_years):
    if age_years < 1:
        months = int(round(age_years * 10))
        return f"{months}mo"
    return f"{age_years:g}"

def get_ai_safety_assessment(title, year):
    if not GEMINI_API_KEY:
        console.print("[yellow]GEMINI_API_KEY missing. Skipping AI assessment.[/]")
        return None

    console.print(f"[yellow]Consulting AI Safety Expert for '{title}'...[/]")

    system_prompt = f"""
You are a safety assessment expert for children's media.
Analyze the show/movie: "{title} ({year})".

Return a valid JSON object with the following boolean or string fields. Do not use Markdown code blocks.

Fields required:
- has_lgbtq (boolean): true if it contains LGBTQ+ themes.
- has_violence (boolean): true if it contains violence or scary imagery.
- is_educational (boolean): true if it is educational.
- reasoning (string): 2-3 sentences on why it is safe/unsafe.
- min_age (number): Absolute minimum safe age (e.g. 0.5, 5).
- max_age (number): Age where kids typically lose interest (e.g. 7, 12).
- stimulation_level (string): "Low", "Medium", or "High".
"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": system_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        response.raise_for_status()

        result = response.json()
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw_text)
    except Exception as e:
        console.print(f"[red]AI Assessment Failed: {e}[/]")
        return None

def load_shows():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_shows(shows):
    with open(DATA_FILE, 'w') as f:
        json.dump(shows, f, indent=2)

def main():
    use_ai = "--no-ai" not in sys.argv
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

        # 2. Fetch Details (IMDb)
        console.print(f"[yellow]Fetching IMDb details for {selected['title']}...[/]")
        details = get_movie_details(selected['id'])

        # 3. Manual Safety Assessment (primary)
        console.rule("[bold green]Safety Assessment[/]")
        tags = []
        if Confirm.ask("Does this show have [bold red]LGBTQ+ Themes[/]?"): tags.append("LGBTQ+ Themes")
        if Confirm.ask("Does it contain [bold red]Violence[/]?"): tags.append("Violence")
        if Confirm.ask("Is it [bold blue]Educational[/]?"): tags.append("Educational")
        reasoning = Prompt.ask("Enter reasoning/opinion (Why is it safe/unsafe?)")
        min_age = parse_age_input("Minimum Age (e.g. 0.5, 3, 7, 6m)")
        max_age = parse_age_input("Maximum Age (e.g. 5, 12, 99, 18m)", default="99")
        stim_level = Prompt.ask("Stimulation Level", choices=["Low", "Medium", "High"], default="Medium")

        # 4. Optional AI Safety Assessment (compare/replace)
        if use_ai and Confirm.ask("Run AI assessment for comparison?", default=False):
            ai_data = get_ai_safety_assessment(selected["title"], selected.get("year", ""))
        else:
            ai_data = None

        if ai_data:
            ai_tags = []
            if ai_data.get("has_lgbtq"): ai_tags.append("LGBTQ+ Themes")
            if ai_data.get("has_violence"): ai_tags.append("Violence")
            if ai_data.get("is_educational"): ai_tags.append("Educational")

            ai_reasoning = ai_data.get("reasoning", "")
            ai_min_age = normalize_age_value(ai_data.get("min_age", 0))
            ai_max_age = normalize_age_value(ai_data.get("max_age", 99))
            ai_stim_level = ai_data.get("stimulation_level", "Medium")

            console.print(Panel(f"""
[bold]AI Assessment:[/bold]
[cyan]Tags:[/cyan] {', '.join(ai_tags) if ai_tags else 'None'}
[cyan]Ages:[/cyan] {ai_min_age} - {ai_max_age}
[cyan]Stimulation:[/cyan] {ai_stim_level}
[cyan]Reasoning:[/cyan] {ai_reasoning}
""", title="Safety Report", border_style="green"))

            if Confirm.ask("Replace manual assessment with AI?", default=False):
                tags = ai_tags
                reasoning = ai_reasoning
                min_age = ai_min_age
                max_age = ai_max_age
                stim_level = ai_stim_level
            elif Confirm.ask("Quick-edit manual fields?", default=False):
                if Confirm.ask("Edit tags?", default=False):
                    tags = []
                    if Confirm.ask("Does this show have [bold red]LGBTQ+ Themes[/]?"): tags.append("LGBTQ+ Themes")
                    if Confirm.ask("Does it contain [bold red]Violence[/]?"): tags.append("Violence")
                    if Confirm.ask("Is it [bold blue]Educational[/]?"): tags.append("Educational")
                if Confirm.ask("Edit ages?", default=False):
                    min_age = parse_age_input("Minimum Age (e.g. 0.5, 3, 7, 6m)", default=str(min_age))
                    max_age = parse_age_input("Maximum Age (e.g. 5, 12, 99, 18m)", default=str(max_age))
                if Confirm.ask("Edit stimulation level?", default=False):
                    stim_level = Prompt.ask("Stimulation Level", choices=["Low", "Medium", "High"], default=stim_level)
                if Confirm.ask("Edit reasoning?", default=False):
                    reasoning = Prompt.ask("Enter reasoning/opinion (Why is it safe/unsafe?)", default=reasoning)

        # Smart Default for Rating
        rating = "Safe"
        if "LGBTQ+ Themes" in tags:
            rating = "Unsafe"
        elif "Violence" in tags:
            rating = "Caution"
        console.print(f"Auto-assigned Rating: [bold cyan]{rating}[/]")

        # Auto-scraped fields (no prompts needed)
        release_year = details.get('year_range', '') or str(selected.get('year', ''))
        runtime = details.get('duration', '')

        console.print(f"Auto-scraped Year: [bold cyan]{release_year}[/]")
        console.print(f"Auto-scraped Runtime: [bold cyan]{runtime if runtime else 'Not found'}[/]")

        new_show = {
            "id": selected['id'],
            "title": selected['title'],
            "synopsis": details['description'],
            "coverImage": details['image'] if details['image'] else selected['image'],
            "cast": details['cast'],
            "tags": tags,
            "featured": False,
            "rating": rating,
            "reasoning": reasoning,
            "ageRecommendation": f"{format_age_label(min_age)}+" if max_age == 99 else f"{format_age_label(min_age)}-{format_age_label(max_age)}",
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
