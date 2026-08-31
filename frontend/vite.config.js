import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server proxies /api to the local FastAPI server, so the frontend and
// backend share an origin and the operator never sees a CORS problem.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8756",
        changeOrigin: false,
      },
    },
  },
  build: {
    outDir: "dist",
  },
});
