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

  it("heads the unit cards with the same axis as the result readout", () => {
    const wrapper = mount(EducationStrip);
    const axis = wrapper.find(".units-axis");
    expect(axis.find(".axis-title").text()).toBe("ISCC-UNITS");
    expect(axis.element.nextElementSibling?.classList.contains("edu-grid")).toBe(true);
    expect(wrapper.findAll(".units-axis")).toHaveLength(1);
  });

  it("keeps the code slot empty and shows the API pointer", () => {
    const wrapper = mount(EducationStrip);
    expect(wrapper.find(".code-bar.slot.idle").text()).toBe("Your ISCC-CODE will land here");
    expect(wrapper.find(".code-bar .iscc-dot").exists()).toBe(true);
    expect(wrapper.text()).not.toMatch(/ISCC:[A-Z2-7]{8,}/);
    expect(wrapper.find(".api-head").text()).toBe("Generate ISO 24138:2024 ISCC-CODEs through the REST API");
    expect(wrapper.find(".api-calls").text()).toContain("POST /api/v1/iscc");
    expect(wrapper.find("a.api-btn").attributes("href")).toBe("/docs");
  });
});
