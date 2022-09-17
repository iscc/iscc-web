// @ts-check
/// <reference types="@prettier/plugin-pug/src/prettier" />

/**
 * @type {import('prettier').Options}
 */
module.exports = {
  // `require.resolve` is needed for e.g. `pnpm`
  plugins: [require.resolve("@prettier/plugin-pug")],

  printWidth: 120,
  arrowParens: "always",

  pugAttributeSeparator: "none",
  pugSingleQuote: false,
  pugClassNotation: "as-is",
  pugWrapAttributesThreshold: 2,
};
