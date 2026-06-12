/** Vitest configuration: frontend component tests run in jsdom via the Vue SFC pipeline. */
import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: "jsdom",
    include: ["frontend/tests/**/*.spec.ts"],
    setupFiles: ["frontend/tests/setup.ts"],
    restoreMocks: true,
  },
});
