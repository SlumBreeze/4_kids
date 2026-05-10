from typing import Optional

from .models import DiscoveredItem, EnrichedItem
from .tmdb_client import TMDBClient


def enrich_from_tmdb(client: TMDBClient, discovered: DiscoveredItem) -> Optional[EnrichedItem]:
    """Fetch full TMDB metadata and normalize it into the app pipeline shape."""
    if discovered.media_type == "tv":
        details = client.get_tv_details(discovered.tmdb_id)
    else:
        details = client.get_movie_details(discovered.tmdb_id)

    external_ids = details.get("external_ids", {})
    imdb_id = external_ids.get("imdb_id")
    if not imdb_id:
        return None

    credits = details.get("credits", {})
    cast = [actor["name"] for actor in credits.get("cast", [])[:3]]
    genres = [genre["name"] for genre in details.get("genres", [])]
    providers = details.get("watch/providers", {})
    platforms = client.extract_platforms(providers)

    if discovered.media_type == "tv":
        certification = client.extract_certification(details.get("content_ratings", {}), "tv")
        episode_runtimes = details.get("episode_run_time", [])
        runtime = client.format_runtime(episode_runtimes[0]) if episode_runtimes else ""
    else:
        certification = client.extract_certification(details.get("release_dates", {}), "movie")
        runtime = client.format_runtime(details.get("runtime"))

    return EnrichedItem(
        tmdb_id=discovered.tmdb_id,
        media_type=discovered.media_type,
        title=discovered.title,
        synopsis=details.get("overview", discovered.overview),
        cover_image_url=client.get_image_url(details.get("poster_path")),
        imdb_id=imdb_id,
        release_year=client.format_year_range(details, discovered.media_type),
        runtime=runtime,
        cast=cast,
        genres=genres,
        certification=certification,
        platforms=platforms,
        popularity=discovered.popularity,
        vote_average=discovered.vote_average,
    )
