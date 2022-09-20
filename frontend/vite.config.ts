import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig(({ command }) => ({
  base: command == "build" ? "/static/dist/" : "/",
  server: {
    origin: "http://127.0.0.1:5173",
  },
  build: {
    manifest: true,
    rollupOptions: {
      input: "frontend/main.ts",
    },
    outDir: "../iscc_web/static/dist/",
    emptyOutDir: true,
  },
  plugins: [vue()],
}));
