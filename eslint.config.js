import pluginVue from "eslint-plugin-vue";
import { defineConfigWithVueTs, vueTsConfigs } from "@vue/eslint-config-typescript";
import prettierConfig from "@vue/eslint-config-prettier";

export default defineConfigWithVueTs(
  { ignores: ["frontend/vite-env.d.ts", "iscc_web/static/dist/**"] },
  pluginVue.configs["flat/essential"],
  vueTsConfigs.recommended,
  {
    rules: {
      "@typescript-eslint/no-unused-vars": "off",
    },
  },
  prettierConfig,
);
