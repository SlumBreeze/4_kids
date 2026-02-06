import { describe, it, expect } from "vitest";
import { filterShows } from "../utils/filter";
import { Show } from "../types";

const mockShows: Show[] = [
  {
    id: "1",
    title: "Old Show",
    releaseYear: "2010",
    minAge: 5,
    maxAge: 10,
    rating: "Safe",
    tags: ["Educational"],
    stimulationLevel: "Low",
    reasoning: "Safe for kids",
    synopsis: "...",
    coverImage: "...",
    cast: [],
    ageRecommendation: "5-10"
  },
  {
    id: "2",
    title: "Unsafe Show",
    releaseYear: "2020",
    minAge: 7,
    maxAge: 12,
    rating: "Unsafe",
    tags: ["LGBTQ+ Themes"],
    stimulationLevel: "Medium",
    reasoning: "Contains themes...",
    synopsis: "...",
    coverImage: "...",
    cast: [],
    ageRecommendation: "7-12"
  },
  {
    id: "3",
    title: "Recent Toddler Show",
    releaseYear: "2022",
    minAge: 0.3,
    maxAge: 2,
    rating: "Safe",
    tags: ["Music"],
    stimulationLevel: "Low",
    reasoning: "Perfect for toddlers",
    synopsis: "...",
    coverImage: "...",
    cast: [],
    ageRecommendation: "3mo-2"
  },
];

describe("Search Bypass Logic", () => {
  it("Search bypasses default constraints (year < 2017)", () => {
    // Default filter (no search, no interaction) should only show ID 3
    const results = filterShows(mockShows, "", undefined, undefined, undefined, undefined, false);
    expect(results.some(s => s.id === "1")).toBe(false);
    expect(results.some(s => s.id === "3")).toBe(true);

    // With search, should see "Old Show" (ID 1)
    const searchResults = filterShows(mockShows, "Old", undefined, undefined, undefined, undefined, false);
    expect(searchResults.some(s => s.id === "1")).toBe(true);
  });

  it("Search bypasses safety ratings (Unsafe shows)", () => {
    // Default filter should NOT show Unsafe (ID 2) because it's not a toddler show
    const results = filterShows(mockShows, "", undefined, undefined, undefined, undefined, false);
    expect(results.some(s => s.id === "2")).toBe(false);

    // With search, should see "Unsafe Show" (ID 2)
    const searchResults = filterShows(mockShows, "Unsafe", undefined, undefined, undefined, undefined, false);
    expect(searchResults.some(s => s.id === "2")).toBe(true);
  });

  it("Search bypasses age bucket filter", () => {
    const searchTerm = "Old";
    const minAge = 0.3;
    const maxAge = 2; // Toddler bucket
    
    const results = filterShows(mockShows, searchTerm, minAge, maxAge, "All", undefined, true);
    
    // "Old Show" is age 5-10, so it's outside 0.3-2. 
    // It should be found because search bypasses the age filter.
    expect(results.some(s => s.id === "1")).toBe(true); 
  });

  it("Search bypasses stimulation filter", () => {
    const searchTerm = "Recent";
    const stimulationLevel = "High";

    const results = filterShows(mockShows, searchTerm, 0.3, 12, stimulationLevel, undefined, true);

    // "Recent Toddler Show" (ID 3) is Low stimulation.
    // It should be found because search bypasses the stimulation filter.
    expect(results.some(s => s.id === "3")).toBe(true);
  });

  it("Clearing search restores default filter application", () => {
    const searchResults = filterShows(mockShows, "Old", 0.3, 2, "All", undefined, false);
    expect(searchResults.some(s => s.id === "1")).toBe(true);

    const clearedResults = filterShows(mockShows, "", 0.3, 2, "All", undefined, false);
    expect(clearedResults.some(s => s.id === "1")).toBe(false);
    expect(clearedResults.some(s => s.id === "3")).toBe(true);
  });
});