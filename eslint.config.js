import pluginVue from "eslint-plugin-vue";
import vueTsEslintConfig from "@vue/eslint-config-typescript";
import prettierConfig from "@vue/eslint-config-prettier";

export default [
  { ignores: ["frontend/vite-env.d.ts"] },
  ...pluginVue.configs["flat/essential"],
  ...vueTsEslintConfig(),
  {
    rules: {
      "@typescript-eslint/no-unused-vars": "off",
    },
  },
  prettierConfig,
];
