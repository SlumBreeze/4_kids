export type ContentTag =
  | "Educational"
  | "Fantasy"
  | "Action"
  | "LGBTQ+ Themes"
  | "Violence"
  | "Scary Imagery"
  | "Values: Friendship"
  | "Values: Family";

export type SafetyRating = "Safe" | "Caution" | "Unsafe";
export type StimulationLevel = "Low" | "Medium" | "High";

export interface Show {
  id: string;
  tmdbId?: string; // NEW: TMDB ID for future updates
  title: string;
  synopsis: string;
  coverImage: string; // URL mock
  cast: string[];
  tags: ContentTag[];
  platforms?: string[]; // NEW: Streaming platforms
  featured?: boolean;
  rating: SafetyRating;
  reasoning: string; // "Why" it's good or bad
  ageRecommendation: string;
  minAge: number; // in Years; decimals under 1 represent months (e.g. 0.5 => 5 months)
  maxAge: number; // in Years
  releaseYear?: string; // "2018" or "2018–Present"
  runtime?: string; // "7 min" or "22 min"
  stimulationLevel?: StimulationLevel;
}
