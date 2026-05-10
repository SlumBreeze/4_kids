import { describe, expect, it } from "vitest";
import { getShowById, getShowsResponse } from "../../server/shows-api.js";

const query = (value: string) => new URLSearchParams(value);

describe("shows API data access", () => {
  it("paginates with default values", () => {
    const response = getShowsResponse(query(""));

    expect(response.items).toHaveLength(25);
    expect(response.limit).toBe(25);
    expect(response.offset).toBe(0);
    expect(response.total).toBeGreaterThan(25);
  });

  it("searches titles case-insensitively", () => {
    const response = getShowsResponse(query("q=bluey&limit=100"));

    expect(response.total).toBeGreaterThan(0);
    expect(response.items.every((show) => show.title.toLowerCase().includes("bluey"))).toBe(true);
  });

  it("filters by overlapping age range", () => {
    const response = getShowsResponse(query("minAge=3&maxAge=5&limit=100"));

    expect(response.total).toBeGreaterThan(0);
    expect(response.items.every((show) => show.minAge <= 5 && show.maxAge >= 3)).toBe(true);
  });

  it("filters by stimulation level and rating", () => {
    const response = getShowsResponse(query("stimulationLevel=Low&rating=Safe&limit=100"));

    expect(response.items.every((show) => show.stimulationLevel === "Low")).toBe(true);
    expect(response.items.every((show) => show.rating === "Safe")).toBe(true);
  });

  it("clamps the maximum limit", () => {
    const response = getShowsResponse(query("limit=500"));

    expect(response.limit).toBe(100);
    expect(response.items.length).toBeLessThanOrEqual(100);
  });

  it("returns one in-scope show by id", () => {
    const list = getShowsResponse(query("q=bluey&limit=1"));
    const show = getShowById(list.items[0].id);

    expect(show?.id).toBe(list.items[0].id);
  });

  it("does not return records outside the 0-5 scope", () => {
    const response = getShowsResponse(query("limit=100&offset=0"));

    expect(response.items.every((show) => show.minAge < 6 && show.maxAge <= 5)).toBe(true);
    expect(response.items.every((show) => show.minAge <= show.maxAge)).toBe(true);
  });
});
