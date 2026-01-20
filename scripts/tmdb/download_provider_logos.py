import os
import urllib.parse
import urllib.request
from typing import Dict, Tuple, List
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(ROOT_DIR, "public", "assets", "providers")
os.makedirs(OUTPUT_DIR, exist_ok=True)
load_dotenv(os.path.join(ROOT_DIR, ".env"))

LOGOS: Dict[str, Tuple[str, str]] = {
    "netflix": ("Netflix", "netflix.com"),
    "disneyplus": ("Disney+", "disneyplus.com"),
    "hulu": ("Hulu", "hulu.com"),
    "primevideo": ("Prime Video", "primevideo.com"),
    "hbomax": ("HBO Max", "hbomax.com"),
    "peacock": ("Peacock", "peacocktv.com"),
    "appletv": ("Apple TV+", "apple.com"),
    "paramountplus": ("Paramount+", "paramountplus.com"),
    "youtubekids": ("YouTube Kids", "youtubekids.com"),
    "roku": ("The Roku Channel", "therokuchannel.com"),
    "tubi": ("Tubi", "tubitv.com"),
    "plutotv": ("Pluto TV", "plutotv.com"),
    "sling": ("Sling TV", "sling.com"),
    "crunchyroll": ("Crunchyroll", "crunchyroll.com"),
    "funimation": ("Funimation", "funimation.com"),
    "noggin": ("Noggin", "noggin.com"),
    "pbskids": ("PBS Kids", "pbskids.org"),
    "nickjr": ("Nick Jr.", "nickjr.com"),
    "cartoonnetwork": ("Cartoon Network", "cartoonnetwork.com"),
    "disneyjunior": ("Disney Junior", "disneyjunior.com"),
    "boomerang": ("Boomerang", "boomerang.com"),
    "discoveryplus": ("Discovery+", "discoveryplus.com"),
    "kidoodle": ("Kidoodle.TV", "kidoodle.tv"),
    "vudu": ("Vudu", "vudu.com"),
    "xumo": ("Xumo", "xumo.com"),
    "kanopy": ("Kanopy", "kanopy.com"),
    "shoutfactory": ("Shout! Factory TV", "shoutfactory.com"),
    "sundancenow": ("Sundance Now", "sundancenow.com"),
    "freevee": ("Freevee", "freevee.com"),
    "yippee": ("Yippee TV", "yippee.tv"),
    "happykids": ("HappyKids TV", "happykids.tv"),
    "hopster": ("Hopster", "hopster.tv"),
    "sesameworkshop": ("Sesame Workshop", "sesameworkshop.org"),
    "pbs": ("PBS", "pbs.org"),
    "familyjr": ("FAMILY Jr.", "familyjr.ca"),
    "retrotv": ("RetroTV", "getafteritmedia.com"),
    "tinypop": ("Tiny Pop", "tinypop.com"),
    "babytv": ("BabyTV", "babytv.com"),
    "toongoggles": ("Toon Goggles", "toongoggles.com"),
    "kidzbop": ("Kidz Bop", "kidzbop.com"),
    "wildbrain": ("WildBrain", "wildbrain.com"),
    "nicktoons": ("Nicktoons", "nicktoons.com"),
    "discoveryfamily": ("Discovery Family", "discoveryfamily.com"),
    "cartoonito": ("Cartoonito", "cartoonito.com"),
    "cbs": ("CBS", "cbs.com"),
}


def download_logo(api_key: str, slug: str, name: str, domain: str) -> Tuple[bool, str]:
    if domain:
        query = domain
    else:
        query = name
    encoded_query = urllib.parse.quote(query)
    url = f"https://img.logo.dev/{encoded_query}?token={api_key}&size=64&format=png"
    output_path = os.path.join(OUTPUT_DIR, f"{slug}.png")

    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            if response.status != 200:
                return False, f"{name} (HTTP {response.status})"

            data = response.read()
            if not data:
                return False, f"{name} (empty response)"

            with open(output_path, "wb") as file_handle:
                file_handle.write(data)

        return True, output_path
    except Exception as exc:
        return False, f"{name} ({exc})"


def main() -> None:
    api_key = os.getenv("LOGO_DEV_API_KEY", "").strip()
    if not api_key:
        print("LOGO_DEV_API_KEY is missing. Add it to your .env or environment.")
        return

    failures: List[str] = []

    for slug, (name, domain) in LOGOS.items():
        success, message = download_logo(api_key, slug, name, domain)
        if not success:
            failures.append(message)

    if failures:
        print("Some logos failed to download:")
        for item in failures:
            print(f"- {item}")
    else:
        print("All logos downloaded successfully.")


if __name__ == "__main__":
    main()
