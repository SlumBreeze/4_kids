import { createServer } from "node:http";
import { resolve } from "node:path";
import { handleShowsApiRequest, serveStaticFile } from "./shows-api.js";

const port = Number.parseInt(process.env.PORT || "4173", 10);
const distPath = resolve(process.cwd(), "dist");

const server = createServer((req, res) => {
  if (handleShowsApiRequest(req, res)) return;
  serveStaticFile(req, res, distPath);
});

server.listen(port, () => {
  console.log(`KidShow Scout server listening on http://localhost:${port}`);
});
