import { SafetyRating, Show, StimulationLevel } from "../types";

export interface ShowsResponse {
  items: Show[];
  total: number;
  limit: number;
  offset: number;
}

export interface ShowQuery {
  q?: string;
  minAge?: number;
  maxAge?: number;
  stimulationLevel?: StimulationLevel | "All";
  rating?: SafetyRating;
  limit?: number;
  offset?: number;
}

export async function fetchShows(
  query: ShowQuery,
  signal?: AbortSignal,
): Promise<ShowsResponse> {
  const params = new URLSearchParams();

  if (query.q) params.set("q", query.q);
  if (query.minAge !== undefined) params.set("minAge", String(query.minAge));
  if (query.maxAge !== undefined) params.set("maxAge", String(query.maxAge));
  if (query.stimulationLevel && query.stimulationLevel !== "All") {
    params.set("stimulationLevel", query.stimulationLevel);
  }
  if (query.rating) params.set("rating", query.rating);
  params.set("limit", String(query.limit ?? 25));
  params.set("offset", String(query.offset ?? 0));

  const response = await fetch(`/api/shows?${params.toString()}`, { signal });

  if (!response.ok) {
    throw new Error(`Failed to fetch shows: ${response.status}`);
  }

  return response.json() as Promise<ShowsResponse>;
}

export async function fetchShow(
  id: string,
  signal?: AbortSignal,
): Promise<Show> {
  const response = await fetch(`/api/shows/${encodeURIComponent(id)}`, { signal });

  if (!response.ok) {
    throw new Error(`Failed to fetch show: ${response.status}`);
  }

  return response.json() as Promise<Show>;
}
