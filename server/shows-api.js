import { createHash } from "node:crypto";
import { createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { brotliCompressSync, gzipSync } from "node:zlib";

const DEFAULT_LIMIT = 25;
const MAX_LIMIT = 100;
const VALID_RATINGS = new Set(["Safe", "Caution", "Unsafe"]);
const VALID_STIMULATION_LEVELS = new Set(["Low", "Medium", "High"]);
const RATING_PRIORITY = {
  Safe: 0,
  Caution: 1,
  Unsafe: 2,
};

const MIME_TYPES = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
};

let cache;

const projectRoot = process.cwd();
const showsPath = resolve(projectRoot, "src/data/shows.json");

const parseInteger = (value, fallback) => {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const parseNumber = (value) => {
  if (value === null || value === undefined || value === "") return undefined;
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : undefined;
};

const releaseYearValue = (releaseYear) => {
  const match = String(releaseYear || "").match(/\d{4}/);
  return match ? Number.parseInt(match[0], 10) : 0;
};

const isInProductScope = (show) => {
  return (
    Number.isFinite(show.minAge) &&
    Number.isFinite(show.maxAge) &&
    show.minAge <= show.maxAge &&
    show.minAge < 6 &&
    show.maxAge <= 5
  );
};

const loadShows = () => {
  const stat = statSync(showsPath);

  if (cache?.mtimeMs === stat.mtimeMs) {
    return cache;
  }

  const raw = readFileSync(showsPath, "utf8");
  const parsed = JSON.parse(raw);
  const scopedShows = parsed.filter(isInProductScope);
  const etag = `"${createHash("sha1").update(raw).digest("hex")}"`;

  cache = {
    etag,
    mtimeMs: stat.mtimeMs,
    shows: scopedShows,
  };

  return cache;
};

export const getShowsResponse = (searchParams) => {
  const { shows } = loadShows();
  const q = searchParams.get("q")?.trim().toLowerCase() || "";
  const minAge = parseNumber(searchParams.get("minAge"));
  const maxAge = parseNumber(searchParams.get("maxAge"));
  const stimulationLevel = searchParams.get("stimulationLevel") || "";
  const rating = searchParams.get("rating") || "";
  const limit = Math.min(
    Math.max(parseInteger(searchParams.get("limit"), DEFAULT_LIMIT), 0),
    MAX_LIMIT,
  );
  const offset = Math.max(parseInteger(searchParams.get("offset"), 0), 0);

  let results = shows;

  if (q) {
    results = results.filter((show) => show.title.toLowerCase().includes(q));
  }

  if (minAge !== undefined) {
    results = results.filter((show) => show.maxAge >= minAge);
  }

  if (maxAge !== undefined) {
    results = results.filter((show) => show.minAge <= maxAge);
  }

  if (VALID_STIMULATION_LEVELS.has(stimulationLevel)) {
    results = results.filter((show) => show.stimulationLevel === stimulationLevel);
  }

  if (VALID_RATINGS.has(rating)) {
    results = results.filter((show) => show.rating === rating);
  }

  results = [...results].sort((a, b) => {
    const ratingDifference =
      (RATING_PRIORITY[a.rating] ?? 1) - (RATING_PRIORITY[b.rating] ?? 1);

    if (ratingDifference !== 0) return ratingDifference;

    const yearDifference = releaseYearValue(b.releaseYear) - releaseYearValue(a.releaseYear);
    if (yearDifference !== 0) return yearDifference;

    const titleDifference = a.title.localeCompare(b.title);
    if (titleDifference !== 0) return titleDifference;

    return a.id.localeCompare(b.id);
  });

  return {
    items: results.slice(offset, offset + limit),
    total: results.length,
    limit,
    offset,
  };
};

export const getShowById = (id) => {
  const { shows } = loadShows();
  return shows.find((show) => show.id === id) || null;
};

const sendJson = (req, res, status, body, etag) => {
  const payload = Buffer.from(JSON.stringify(body));
  const accepts = req.headers["accept-encoding"] || "";
  let encoded = payload;
  let encoding;

  if (accepts.includes("br")) {
    encoded = brotliCompressSync(payload);
    encoding = "br";
  } else if (accepts.includes("gzip")) {
    encoded = gzipSync(payload);
    encoding = "gzip";
  }

  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=300");
  res.setHeader("Vary", "Accept-Encoding");
  if (etag) res.setHeader("ETag", etag);
  if (encoding) res.setHeader("Content-Encoding", encoding);
  res.end(encoded);
};

export const handleShowsApiRequest = (req, res) => {
  const url = new URL(req.url || "/", "http://localhost");

  if (req.method !== "GET" || !url.pathname.startsWith("/api/shows")) {
    return false;
  }

  const { etag } = loadShows();

  if (req.headers["if-none-match"] === etag) {
    res.statusCode = 304;
    res.setHeader("Cache-Control", "public, max-age=300");
    res.setHeader("ETag", etag);
    res.end();
    return true;
  }

  if (url.pathname === "/api/shows") {
    sendJson(req, res, 200, getShowsResponse(url.searchParams), etag);
    return true;
  }

  const match = url.pathname.match(/^\/api\/shows\/([^/]+)$/);
  if (match) {
    const show = getShowById(decodeURIComponent(match[1]));

    if (!show) {
      sendJson(req, res, 404, { error: "Show not found" }, etag);
      return true;
    }

    sendJson(req, res, 200, show, etag);
    return true;
  }

  sendJson(req, res, 404, { error: "Not found" }, etag);
  return true;
};

export const serveStaticFile = (req, res, publicRoot) => {
  const url = new URL(req.url || "/", "http://localhost");
  const requestedPath = url.pathname === "/" ? "/index.html" : decodeURIComponent(url.pathname);
  const filePath = resolve(publicRoot, `.${requestedPath}`);
  const fallbackPath = join(publicRoot, "index.html");
  const targetPath = filePath.startsWith(publicRoot) && existsSync(filePath) ? filePath : fallbackPath;

  if (!targetPath.startsWith(publicRoot) || !existsSync(targetPath)) {
    res.statusCode = 404;
    res.end("Not found");
    return;
  }

  res.statusCode = 200;
  res.setHeader("Content-Type", MIME_TYPES[extname(targetPath)] || "application/octet-stream");
  createReadStream(targetPath).pipe(res);
};
