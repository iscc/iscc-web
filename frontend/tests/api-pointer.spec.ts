/** Tests for the navy API pointer below the first-visit panel and the result feed. */
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ApiPointer from "../components/ApiPointer.vue";

describe("ApiPointer", () => {
  it("names the REST calls and links the API reference", () => {
    const wrapper = mount(ApiPointer);
    expect(wrapper.find(".api-head").text()).toBe("Generate ISO 24138:2024 ISCCs through the REST API");
    expect(wrapper.find(".api-calls").text()).toBe(
      "POST /api/v1/iscc · GET /api/v1/explain/{iscc} · POST /api/v1/simprint",
    );
    const link = wrapper.find("a.api-btn");
    expect(link.attributes("href")).toBe("/docs");
    expect(link.text()).toBe("Open API docs");
  });

  it("is a dark panel with the thin secondary button", () => {
    const wrapper = mount(ApiPointer);
    expect(wrapper.classes()).toContain("on-dark");
    expect(wrapper.find("a.api-btn").classes()).toEqual(
      expect.arrayContaining(["iscc-btn--secondary", "iscc-btn--thin"]),
    );
  });
});
