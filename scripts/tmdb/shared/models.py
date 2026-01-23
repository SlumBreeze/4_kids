from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class DiscoveredItem:
    """Raw discovery result from TMDB API"""
    tmdb_id: int
    media_type: str  # "tv" or "movie"
    title: str
    original_title: str
    overview: str  # Synopsis preview
    poster_path: Optional[str]
    release_date: Optional[str]  # First air date or release date
    vote_average: float
    vote_count: int
    popularity: float
    genre_ids: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tmdb_id': self.tmdb_id,
            'media_type': self.media_type,
            'title': self.title,
            'original_title': self.original_title,
            'overview': self.overview,
            'poster_path': self.poster_path,
            'release_date': self.release_date,
            'vote_average': self.vote_average,
            'vote_count': self.vote_count,
            'popularity': self.popularity,
            'genre_ids': self.genre_ids
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiscoveredItem':
        return cls(**data)


@dataclass
class EnrichedItem:
    """Full metadata from TMDB detail endpoints"""
    # From discovery
    tmdb_id: int
    media_type: str

    # Core metadata
    title: str
    synopsis: str  # Full overview
    cover_image_url: str  # Full w500 URL

    # Additional details
    imdb_id: Optional[str]  # tt12345678
    release_year: Optional[str]  # "2018–Present" or "2020–2023"
    runtime: Optional[str]  # "22 min" or "1 hr 30 min"
    cast: List[str]  # Top 3 actors
    genres: List[str]  # ["Animation", "Family"]
    certification: Optional[str]  # "TV-Y", "G", "PG"
    platforms: List[str]  # ["Netflix", "Disney+", "Hulu"]

    # Metadata
    popularity: float
    vote_average: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tmdb_id': self.tmdb_id,
            'media_type': self.media_type,
            'title': self.title,
            'synopsis': self.synopsis,
            'cover_image_url': self.cover_image_url,
            'imdb_id': self.imdb_id,
            'release_year': self.release_year,
            'runtime': self.runtime,
            'cast': self.cast,
            'genres': self.genres,
            'certification': self.certification,
            'platforms': self.platforms,
            'popularity': self.popularity,
            'vote_average': self.vote_average
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnrichedItem':
        return cls(**data)


@dataclass
class AIAssessment:
    """Gemini AI safety assessment"""
    rating: str  # "Safe", "Caution", "Unsafe"
    min_age: float
    max_age: float
    stimulation_level: str  # "Low", "Medium", "High"
    has_lgbtq: bool
    has_violence: bool
    has_scary: bool
    is_educational: bool
    reasoning: str
    safe_above_age: Optional[float] = None  # Age where Caution becomes Safe
    is_episodic_issue: bool = False  # True if flags only apply to isolated episodes

    def needs_review(self) -> bool:
        """Flag items requiring human review"""
        return (
            self.has_lgbtq or
            (self.has_violence and self.min_age < 7) or
            self.rating in ["Unsafe", "Caution"] or
            len(self.reasoning) < 50
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rating': self.rating,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'stimulation_level': self.stimulation_level,
            'has_lgbtq': self.has_lgbtq,
            'has_violence': self.has_violence,
            'has_scary': self.has_scary,
            'is_educational': self.is_educational,
            'reasoning': self.reasoning,
            'safe_above_age': self.safe_above_age,
            'is_episodic_issue': self.is_episodic_issue
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIAssessment':
        return cls(
            rating=data['rating'],
            min_age=data['min_age'],
            max_age=data['max_age'],
            stimulation_level=data['stimulation_level'],
            has_lgbtq=data['has_lgbtq'],
            has_violence=data['has_violence'],
            has_scary=data['has_scary'],
            is_educational=data['is_educational'],
            reasoning=data['reasoning'],
            safe_above_age=data.get('safe_above_age'),
            is_episodic_issue=data.get('is_episodic_issue', False)
        )


@dataclass
class AssessedItem:
    """Enriched item + AI assessment"""
    enriched: EnrichedItem
    assessment: AIAssessment
    flagged_for_review: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            'enriched': self.enriched.to_dict(),
            'assessment': self.assessment.to_dict(),
            'flagged_for_review': self.flagged_for_review
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssessedItem':
        return cls(
            enriched=EnrichedItem.from_dict(data['enriched']),
            assessment=AIAssessment.from_dict(data['assessment']),
            flagged_for_review=data['flagged_for_review']
        )


@dataclass
class ReviewedItem:
    """Human-reviewed and approved item"""
    enriched: EnrichedItem

    # Human-edited fields
    rating: str
    tags: List[str]
    reasoning: str
    min_age: float
    max_age: float
    stimulation_level: str
    featured: bool
    safe_above_age: Optional[float] = None  # Age where Caution becomes Safe
    is_episodic_issue: bool = False  # True if flags only apply to isolated episodes

    # Audit trail
    ai_suggestion: Optional[AIAssessment] = None
    reviewed_at: str = ""  # ISO timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            'enriched': self.enriched.to_dict(),
            'rating': self.rating,
            'tags': self.tags,
            'reasoning': self.reasoning,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'stimulation_level': self.stimulation_level,
            'featured': self.featured,
            'safe_above_age': self.safe_above_age,
            'is_episodic_issue': self.is_episodic_issue,
            'ai_suggestion': self.ai_suggestion.to_dict() if self.ai_suggestion else None,
            'reviewed_at': self.reviewed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReviewedItem':
        ai_suggestion = None
        if data.get('ai_suggestion'):
            ai_suggestion = AIAssessment.from_dict(data['ai_suggestion'])

        return cls(
            enriched=EnrichedItem.from_dict(data['enriched']),
            rating=data['rating'],
            tags=data['tags'],
            reasoning=data['reasoning'],
            min_age=data['min_age'],
            max_age=data['max_age'],
            stimulation_level=data['stimulation_level'],
            featured=data['featured'],
            safe_above_age=data.get('safe_above_age'),
            is_episodic_issue=data.get('is_episodic_issue', False),
            ai_suggestion=ai_suggestion,
            reviewed_at=data['reviewed_at']
        )

    def to_show_format(self) -> Dict[str, Any]:
        """Convert to final Show schema"""
        from .io_utils import format_age_label

        min_label = format_age_label(self.min_age)
        if self.max_age >= 99:
            age_recommendation = f"{min_label}+"
        else:
            max_label = format_age_label(self.max_age)
            age_recommendation = f"{min_label}-{max_label}"

        return {
            "id": self.enriched.imdb_id,
            "tmdbId": str(self.enriched.tmdb_id),
            "title": self.enriched.title,
            "synopsis": self.enriched.synopsis,
            "coverImage": self.enriched.cover_image_url,
            "cast": self.enriched.cast,
            "tags": self.tags,
            "platforms": self.enriched.platforms,
            "rating": self.rating,
            "reasoning": self.reasoning,
            "ageRecommendation": age_recommendation,
            "minAge": self.min_age,
            "maxAge": self.max_age,
            "safeAboveAge": self.safe_above_age,
            "isEpisodicIssue": self.is_episodic_issue,
            "releaseYear": self.enriched.release_year,
            "runtime": self.enriched.runtime,
            "stimulationLevel": self.stimulation_level,
            "featured": self.featured
        }

