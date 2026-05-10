import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { handleShowsApiRequest } from "./server/shows-api.js";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: "shows-api",
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (handleShowsApiRequest(req, res)) return;
          next();
        });
      },
      configurePreviewServer(server) {
        server.middlewares.use((req, res, next) => {
          if (handleShowsApiRequest(req, res)) return;
          next();
        });
      },
    },
  ],
});
