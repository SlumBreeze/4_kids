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

export const filterShows = (
  shows: Show[],
  searchTerm: string,
  viewerAge?: number,
): Show[] => {
  // 1. Classify all shows (Applying the policy with age context)
  const classifiedShows = shows.map((show) => classifyShow(show, viewerAge));

  // 2. Filter by search term
  if (!searchTerm) return classifiedShows;

  return classifiedShows.filter((s) =>
    s.title.toLowerCase().includes(searchTerm.toLowerCase()),
  );
};
