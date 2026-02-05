import { describe, it, expect } from "vitest";
import { Show } from "../types";
import { sortShows, filterShows } from "../utils/filter";

describe("sortShows", () => {
  const mockShows: Partial<Show>[] = [
    { id: "1", title: "Old Safe", rating: "Safe", releaseYear: "2010" },
    { id: "2", title: "New Safe", rating: "Safe", releaseYear: "2023" },
    { id: "3", title: "New Caution", rating: "Caution", releaseYear: "2024" },
    { id: "4", title: "Old Caution", rating: "Caution", releaseYear: "2015" },
    { id: "5", title: "Unsafe", rating: "Unsafe", releaseYear: "2025" },
  ];

  it("should sort by Safe, then Caution, then by Release Year Descending", () => {
    const sorted = sortShows(mockShows as Show[]);
    
    // Expected order:
    // 1. New Safe (2023)
    // 2. Old Safe (2010)
    // 3. New Caution (2024)
    // 4. Old Caution (2015)
    // 5. Unsafe (2025)
    
    expect(sorted[0].title).toBe("New Safe");
    expect(sorted[1].title).toBe("Old Safe");
    expect(sorted[2].title).toBe("New Caution");
    expect(sorted[3].title).toBe("Old Caution");
    expect(sorted[4].title).toBe("Unsafe");
  });

  it("should handle releaseYear ranges by using the starting year", () => {
    const shows: Partial<Show>[] = [
      { id: "1", title: "Range 2018", rating: "Safe", releaseYear: "2018–Present" },
      { id: "2", title: "Single 2020", rating: "Safe", releaseYear: "2020" },
    ];
    const sorted = sortShows(shows as Show[]);
    expect(sorted[0].title).toBe("Single 2020");
    expect(sorted[1].title).toBe("Range 2018");
  });
});

describe("filterShows enhanced", () => {
  const mockShows: Partial<Show>[] = [
    { id: "1", title: "New Show", releaseYear: "2020", rating: "Safe", tags: [] },
    { id: "2", title: "Old Show", releaseYear: "2010", rating: "Safe", tags: [] },
    { id: "3", title: "Bluey", releaseYear: "2018", rating: "Safe", tags: [] },
  ];

  it("should apply 2017+ constraint by default (no search, no interaction)", () => {
    // We'll need to update filterShows signature to accept a context/interaction flag
    const filtered = filterShows(mockShows as Show[], "", undefined, false);
    expect(filtered.length).toBe(2);
    expect(filtered.find(s => s.title === "Old Show")).toBeUndefined();
  });

  it("should bypass 2017+ constraint when search term is provided", () => {
    const filtered = filterShows(mockShows as Show[], "Old", undefined, true);
    expect(filtered.length).toBe(1);
    expect(filtered[0].title).toBe("Old Show");
  });

  it("should bypass 2017+ constraint when user has interacted with filters", () => {
    const filtered = filterShows(mockShows as Show[], "", undefined, true);
    expect(filtered.length).toBe(3);
    expect(filtered.find(s => s.title === "Old Show")).toBeDefined();
  });
});
