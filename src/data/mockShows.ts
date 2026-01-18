import { Show } from "../types";
import showsData from "./shows.json";

// We assert the type because JSON import might be inferred loosely
export const mockShows: Show[] = showsData as unknown as Show[];
