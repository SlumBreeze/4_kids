import argparse
from typing import Any, Dict, List

from shared.config import SHOWS_FILE
from shared.io_utils import load_json, save_json, format_age_label


def age_recommendation(min_age: float, max_age: float) -> str:
    min_label = format_age_label(min_age)
    if max_age >= 5:
        return f"{min_label}+"
    return f"{min_label}-{format_age_label(max_age)}"


def normalize_show(show: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(show)
    min_age = float(normalized.get("minAge", 0))
    max_age = float(normalized.get("maxAge", 5))

    if max_age > 5:
        max_age = 5.0
    if min_age > max_age:
        min_age = max_age

    normalized["minAge"] = min_age
    normalized["maxAge"] = max_age
    normalized["ageRecommendation"] = age_recommendation(min_age, max_age)
    return normalized


def find_issues(shows: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "minAge>=6": sum(1 for show in shows if float(show.get("minAge", 0)) >= 6),
        "maxAge>5": sum(1 for show in shows if float(show.get("maxAge", 0)) > 5),
        "minAge>maxAge": sum(
            1
            for show in shows
            if float(show.get("minAge", 0)) > float(show.get("maxAge", 0))
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and optionally normalize shows.json.")
    parser.add_argument("--fix", action="store_true", help="Write normalized ages back to shows.json.")
    args = parser.parse_args()

    shows = load_json(SHOWS_FILE) or []
    before = find_issues(shows)
    print(f"Loaded {len(shows)} shows")
    print(f"Before: {before}")

    if not args.fix:
        return

    normalized = [normalize_show(show) for show in shows]
    after = find_issues(normalized)
    save_json(SHOWS_FILE, normalized)
    print(f"After: {after}")
    print(f"Updated {SHOWS_FILE}")


if __name__ == "__main__":
    main()
