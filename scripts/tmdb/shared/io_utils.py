import json
import os
from typing import List, Optional

def load_json(filepath: str) -> Optional[List]:
    """Load JSON file or return None"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath: str, data: List):
    """Save data to JSON file with pretty formatting"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_age_value(value) -> float:
    """Normalize age input (same as add_show.py)"""
    try:
        age = float(value)
    except (TypeError, ValueError):
        return 0.0
    if age < 0:
        return 0.0
    if age < 1:
        # Interpret decimal as months in tenths: 0.4 -> 4 months, 0.5 -> 5 months
        months = int(round(age * 10))
        return months / 10
    return age

def parse_age_input(label: str, default=None) -> float:
    """Parse age input from user (same as add_show.py)"""
    from rich.prompt import Prompt

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

def format_age_label(age_years: float) -> str:
    """Format age for display (same as add_show.py)"""
    if age_years < 1:
        months = int(round(age_years * 10))
        return f"{months}mo"
    return f"{age_years:g}"
