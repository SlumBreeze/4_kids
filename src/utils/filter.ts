import { Show } from "../types";

export const classifyShow = (show: Show, viewerAge?: number): Show => {
  const newShow = { ...show };

  // STRICT POLICY ENFORCEMENT - LGBTQ+ always Unsafe (per user requirement)
  if (show.tags.includes("LGBTQ+ Themes")) {
    // Exception: If the issue is isolated to specific episodes, downgrade to Caution
    if (show.isEpisodicIssue) {
      newShow.rating = "Caution";
      newShow.reasoning +=
        " (Note: Contains isolated episodes with LGBTQ+ themes)";
    } else {
      newShow.rating = "Unsafe";
      newShow.reasoning =
        "Contains themes that do not align with family-friendly values.";
      return newShow;
    }
  }

  // Age-aware Caution logic for Violence/Scary content
  if (show.tags.includes("Violence") || show.tags.includes("Scary Imagery")) {
    const safeAbove = show.safeAboveAge ?? 7; // Default threshold if not set

    if (viewerAge !== undefined && viewerAge >= safeAbove) {
      // Viewer is old enough — content is Safe for them
      newShow.rating = "Safe";
    } else {
      // Viewer is too young or no age specified — default to Caution
      if (newShow.rating !== "Unsafe") {
        newShow.rating = "Caution";
      }
    }
  }

  return newShow;
};

export const sortShows = (shows: Show[]): Show[] => {
  const getYear = (yearStr?: string): number => {
    if (!yearStr) return 0;
    // Extract first 4 digits (handles "2018" or "2018–Present")
    const match = yearStr.match(/\d{4}/);
    return match ? parseInt(match[0], 10) : 0;
  };

  const ratingPriority = {
    Safe: 0,
    Caution: 1,
    Unsafe: 2,
  };

  return [...shows].sort((a, b) => {
    // 1. Primary: Rating (Safe < Caution < Unsafe)
    const pA = ratingPriority[a.rating];
    const pB = ratingPriority[b.rating];
    if (pA !== pB) return pA - pB;

    // 2. Secondary: Release Year (Descending)
    return getYear(b.releaseYear) - getYear(a.releaseYear);
  });
};

export const filterShows = (
  shows: Show[],
  searchTerm: string,
  minAge?: number,
  maxAge?: number,
  stimulationLevel?: string,
  viewerAge?: number,
  isInteracted: boolean = false,
): Show[] => {
  // 1. Classify all shows (Applying the policy with age context)
  let classifiedShows = shows.map((show) => classifyShow(show, viewerAge));

  const isSearching = !!searchTerm.trim();

  // 2. Apply Filters (Bypassed if searching)
  if (!isSearching) {
    // Default Constraints (unless user interacted)
    if (!isInteracted) {
      classifiedShows = classifiedShows.filter((show) => {
        // Recency: 2017+
        const match = show.releaseYear?.match(/\d{4}/);
        const year = match ? parseInt(match[0], 10) : 0;
        const isRecent = year >= 2017;

        // Age: 3mo - 2yr (0.3 - 2.0)
        const isToddler = show.minAge <= 2.0 && show.maxAge >= 0.3;

        return isRecent && isToddler;
      });
    }

    // Age Bucket Filter
    if (minAge !== undefined && maxAge !== undefined) {
      classifiedShows = classifiedShows.filter((show) => {
        return show.minAge <= maxAge && show.maxAge >= minAge;
      });
    }

    // Stimulation Filter
    if (stimulationLevel && stimulationLevel !== "All") {
      classifiedShows = classifiedShows.filter((show) => {
        const stim = (show.stimulationLevel || "Medium") as StimulationLevel;
        return stim === stimulationLevel;
      });
    }
  }

  // 3. Filter by search term
  if (!isSearching) return classifiedShows;

  return classifiedShows.filter((s) =>
    s.title.toLowerCase().includes(searchTerm.toLowerCase()),
  );
};
