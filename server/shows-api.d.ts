export function getShowsResponse(searchParams: URLSearchParams): {
  items: unknown[];
  total: number;
  limit: number;
  offset: number;
};

export function getShowById(id: string): unknown | null;

export function handleShowsApiRequest(req: unknown, res: unknown): boolean;

export function serveStaticFile(
  req: unknown,
  res: unknown,
  publicRoot: string,
): void;
