import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import * as path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ command }) => ({
  base: command == "build" ? "/static/dist/" : "/",
  server: {
    origin: "http://127.0.0.1:5173",
  },
  resolve: {
    alias: {
      "~bootstrap": path.resolve(__dirname, "../node_modules/bootstrap"),
    },
  },
  build: {
    manifest: true,
    rollupOptions: {
      input: (command == "build" ? "frontend/" : "") + "main.ts",
    },
    outDir: "../iscc_web/static/dist/",
    emptyOutDir: true,
  },
  plugins: [vue()],
}));
