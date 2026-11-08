/** Tests for the navy footer: the small white ISCC logo, legal pages and developer exits. */
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import AppFooter from "../components/AppFooter.vue";

describe("AppFooter", () => {
  it("carries the white-only ISCC logo without the product name", () => {
    const logo = mount(AppFooter).find("img.logo");
    expect(logo.attributes("alt")).toBe("ISCC");
    // Small enough for Vite to inline as a data URI, whose SVG ids still name the master.
    const src = logo.attributes("src");
    expect(src).toContain("iscc-logo-white-title");
    expect(src).not.toMatch(/F56169/i); // no coral circle
    expect(src).not.toContain("generator");
  });

  it("links to the legal pages on iscc.io", () => {
    const links = mount(AppFooter)
      .findAll("a.legal")
      .map((a) => [a.text(), a.attributes("href")]);
    expect(links).toEqual([
      ["Privacy Policy", "https://iscc.io/privacy"],
      ["Cookie Policy", "https://iscc.io/cookies"],
      ["Imprint", "https://iscc.io/imprint"],
    ]);
  });

  it("links to the API docs and the source code", () => {
    const hrefs = mount(AppFooter)
      .findAll("a.exit")
      .map((a) => a.attributes("href"));
    expect(hrefs).toEqual(["/docs", "https://github.com/iscc/iscc-web"]);
  });
});
