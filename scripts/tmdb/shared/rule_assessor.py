import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .models import AIAssessment, EnrichedItem


@dataclass
class RuleMatch:
    category: str
    terms: List[str]


LGBTQ_TERMS = [
    "lgbt",
    "lgbtq",
    "gay",
    "lesbian",
    "bisexual",
    "transgender",
    "nonbinary",
    "non-binary",
    "queer",
    "same-sex",
    "two moms",
    "two dads",
    "pride parade",
    "drag queen",
]

VIOLENCE_TERMS = [
    "battle",
    "combat",
    "fight",
    "fighting",
    "martial arts",
    "mutant",
    "ninja",
    "robot war",
    "shoot",
    "weapon",
    "war",
]

SCARY_TERMS = [
    "ghost",
    "haunted",
    "horror",
    "monster",
    "nightmare",
    "scary",
    "spooky",
    "villain",
    "zombie",
]

EDUCATIONAL_TERMS = [
    "alphabet",
    "counting",
    "educational",
    "learn",
    "learning",
    "letters",
    "numbers",
    "preschool",
    "science",
    "social-emotional",
]

HIGH_STIMULATION_TERMS = [
    "action",
    "adventure",
    "battle",
    "fight",
    "ninja",
    "robot",
    "superhero",
]

LOW_STIMULATION_TERMS = [
    "bedtime",
    "calm",
    "gentle",
    "lullaby",
    "quiet",
    "sleep",
]

SAFE_CERTIFICATIONS = {"G", "TV-G", "TV-Y"}
CAUTION_CERTIFICATIONS = {"PG", "TV-PG", "TV-Y7", "TV-Y7-FV"}
UNSAFE_CERTIFICATIONS = {"PG-13", "TV-14", "R", "NC-17", "TV-MA"}


def evidence_text(item: EnrichedItem) -> str:
    fields = [
        item.title,
        item.synopsis,
        item.certification or "",
        " ".join(item.genres or []),
    ]
    return " ".join(fields).casefold()


def find_terms(text: str, terms: List[str]) -> List[str]:
    matches = []
    for term in terms:
        pattern = r"(?<![a-z0-9])" + re.escape(term.casefold()) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            matches.append(term)
    return matches


def matched_rules(item: EnrichedItem) -> Dict[str, List[str]]:
    text = evidence_text(item)
    return {
        "lgbtq": find_terms(text, LGBTQ_TERMS),
        "violence": find_terms(text, VIOLENCE_TERMS),
        "scary": find_terms(text, SCARY_TERMS),
        "educational": find_terms(text, EDUCATIONAL_TERMS),
        "high_stimulation": find_terms(text, HIGH_STIMULATION_TERMS),
        "low_stimulation": find_terms(text, LOW_STIMULATION_TERMS),
    }


def certification_rating(certification: str) -> str:
    cert = (certification or "").strip().upper()
    if cert in UNSAFE_CERTIFICATIONS:
        return "Unsafe"
    if cert in CAUTION_CERTIFICATIONS:
        return "Caution"
    return "Safe"


def stimulation_level(matches: Dict[str, List[str]]) -> str:
    if matches["high_stimulation"]:
        return "High"
    if matches["low_stimulation"]:
        return "Low"
    return "Medium"


def age_bounds(rating: str, matches: Dict[str, List[str]], certification: str) -> Tuple[float, float, float | None]:
    cert = (certification or "").strip().upper()
    if rating == "Unsafe":
        return 0.3, 5.0, None
    if matches["violence"] or matches["scary"] or cert in CAUTION_CERTIFICATIONS:
        return 4.0, 5.0, 5.0
    if matches["educational"]:
        return 0.3, 5.0, None
    return 2.0, 5.0, None


def reasoning_for(item: EnrichedItem, rating: str, matches: Dict[str, List[str]]) -> str:
    evidence = []
    for label in ["lgbtq", "violence", "scary", "educational"]:
        if matches[label]:
            evidence.append(f"{label}: {', '.join(matches[label])}")

    cert = item.certification or "unrated"
    if evidence:
        evidence_text_value = "; ".join(evidence)
    else:
        evidence_text_value = "no explicit concern keywords found in title, synopsis, genres, or certification"

    return (
        f"Rule-based assessment from TMDB metadata. Certification is {cert}; "
        f"matched evidence: {evidence_text_value}. Rating is {rating}; records with concern matches should be manually reviewed."
    )


def assess_with_rules(item: EnrichedItem) -> AIAssessment:
    matches = matched_rules(item)
    rating = certification_rating(item.certification or "")

    if matches["lgbtq"]:
        rating = "Unsafe"
    elif matches["violence"] or matches["scary"]:
        rating = "Caution" if rating != "Unsafe" else rating

    min_age, max_age, safe_above_age = age_bounds(rating, matches, item.certification or "")

    return AIAssessment(
        rating=rating,
        min_age=min_age,
        max_age=max_age,
        stimulation_level=stimulation_level(matches),
        has_lgbtq=bool(matches["lgbtq"]),
        has_violence=bool(matches["violence"]),
        has_scary=bool(matches["scary"]),
        is_educational=bool(matches["educational"]),
        reasoning=reasoning_for(item, rating, matches),
        safe_above_age=safe_above_age,
        is_episodic_issue=False,
    )
