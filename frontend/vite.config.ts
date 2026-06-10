import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// https://vitejs.dev/config/
export default defineConfig(({ command }) => ({
  base: command == "build" ? "/static/dist/" : "/",
  server: {
    origin: "http://localhost:5173",
    cors: true,
  },
  resolve: {
    alias: {
      "~bootstrap": path.resolve(__dirname, "../node_modules/bootstrap"),
    },
  },
  build: {
    // iscc_web/vite.py expects the manifest at static/dist/manifest.json (not .vite/manifest.json)
    manifest: "manifest.json",
    rollupOptions: {
      input: path.resolve(__dirname, "main.ts"),
    },
    outDir: "../iscc_web/static/dist/",
    emptyOutDir: true,
  },
  css: {
    preprocessorOptions: {
      scss: {
        // Bootstrap 5.3 still uses @import and legacy color functions internally
        silenceDeprecations: ["if-function", "color-functions", "import", "global-builtin"],
      },
    },
  },
  plugins: [vue()],
}));
