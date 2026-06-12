/** Tests for the first-visit education strip. */
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import EducationStrip from "../components/EducationStrip.vue";

describe("EducationStrip", () => {
  it("teaches all five layers in axis order", () => {
    const wrapper = mount(EducationStrip);
    const cards = wrapper.findAll(".edu-card");
    expect(cards).toHaveLength(5);
    expect(cards.map((c) => c.find(".edu-name").text())).toEqual([
      "Meta-Code",
      "Semantic-Code",
      "Content-Code",
      "Data-Code",
      "Instance-Code",
    ]);
  });

  it("shows a sample composite code and the API pointer", () => {
    const wrapper = mount(EducationStrip);
    expect(wrapper.find(".sample-bar").text()).toMatch(/^ISCC:[A-Z2-7]+$/);
    expect(wrapper.find(".api-calls").text()).toContain("POST /api/v1/iscc");
    expect(wrapper.find("a.api-btn").attributes("href")).toBe("/docs");
  });
});
