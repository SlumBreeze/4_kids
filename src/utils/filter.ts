import { Show } from "../types";

export const classifyShow = (show: Show): Show => {
  const newShow = { ...show };

  // STRICT POLICY ENFORCEMENT
  if (show.tags.includes("LGBTQ+ Themes")) {
    newShow.rating = "Unsafe";
    newShow.reasoning =
      "Contains themes that do not align with family-friendly values.";
  } else if (
    show.tags.includes("Violence") ||
    show.tags.includes("Scary Imagery")
  ) {
    // Keep existing caution rating if set, otherwise default to Caution
    if (newShow.rating !== "Unsafe") {
      newShow.rating = "Caution";
    }
  }

  return newShow;
};

export const filterShows = (shows: Show[], searchTerm: string): Show[] => {
  // 1. Classify all shows (Applying the policy)
  const classifiedShows = shows.map(classifyShow);

  // 2. Filter by search term
  if (!searchTerm) return classifiedShows;

  return classifiedShows.filter(
    (s) =>
      s.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.tags.some((t) => t.toLowerCase().includes(searchTerm.toLowerCase())),
  );
};
