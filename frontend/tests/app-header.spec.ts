/** Tests for the navy top bar: the ISCC generator project logo and the developer exits. */
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import AppHeader from "../components/AppHeader.vue";

describe("AppHeader", () => {
  it("shows the generator project logo, with the plain ISCC logo for phones", () => {
    const wrapper = mount(AppHeader);
    const lockup = wrapper.find("img.lockup");
    expect(lockup.attributes("alt")).toBe("ISCC generator");
    expect(lockup.attributes("src")).toContain("iscc-generator-white-coral.svg");
    expect(lockup.classes()).toEqual(expect.arrayContaining(["d-none", "d-sm-block"]));
    const logo = wrapper.find("img.logo");
    expect(logo.attributes("alt")).toBe("ISCC");
    // Small enough for Vite to inline as a data URI, whose SVG ids still name the master.
    expect(logo.attributes("src")).toContain("iscc-logo-white-coral");
    expect(logo.classes()).toContain("d-sm-none");
  });

  it("sets no product name in live text", () => {
    expect(mount(AppHeader).text()).not.toMatch(/generator/i);
  });

  it("links to the API docs", () => {
    expect(mount(AppHeader).find('a[href="/docs"]').text()).toBe("API Docs");
  });
});
