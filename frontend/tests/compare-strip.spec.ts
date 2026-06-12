/** Tests for the diff readout: percentages, bit coloring, verdict and report. */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import CompareStrip from "../components/CompareStrip.vue";
import { makeExplain, makeSpecimen, makeUnit } from "./fixtures";

const flip = (bits: string, count: number) =>
  bits
    .split("")
    .map((b, i) => (i < count ? (b === "1" ? "0" : "1") : b))
    .join("");

const pair = () => {
  const meta = makeUnit("meta");
  const content = makeUnit("content");
  const data = makeUnit("data");
  const instance = makeUnit("instance");
  const a = makeSpecimen({ id: "a", label: "original.jpg", explain: makeExplain([meta, content, data, instance]) });
  const b = makeSpecimen({
    id: "b",
    label: "copy.jpg",
    explain: makeExplain([
      makeUnit("meta", { bits: flip(meta.hash_bits, 26) }),
      makeUnit("content", { bits: flip(content.hash_bits, 3) }),
      makeUnit("data", { bits: flip(data.hash_bits, 9) }),
      makeUnit("instance", { bits: flip(instance.hash_bits, 31) }),
    ]),
  });
  return { a, b };
};

beforeEach(() => {
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText: vi.fn().mockResolvedValue(undefined) },
    configurable: true,
  });
});

describe("CompareStrip", () => {
  it("renders per-layer match percentages from Hamming distance", () => {
    const { a, b } = pair();
    const wrapper = mount(CompareStrip, { props: { a, b } });
    const cards = wrapper.findAll(".diff-card");
    expect(cards).toHaveLength(4);
    // 64-bit units: 26/3/9/31 flipped bits -> 59%, 95%, 86%, 52%
    expect(cards[0].find(".dc-pct").text()).toBe("59%");
    expect(cards[1].find(".dc-pct").text()).toBe("95%");
    expect(cards[2].find(".dc-pct").text()).toBe("86%");
    expect(cards[3].find(".dc-pct").text()).toBe("52%");
    wrapper.unmount();
  });

  it("renders two aligned bit strips per layer with equal/diff status colors", () => {
    const { a, b } = pair();
    const wrapper = mount(CompareStrip, { props: { a, b } });
    const content = wrapper.findAll(".diff-card")[1];
    const strips = content.findAll(".dc-bits");
    expect(strips).toHaveLength(2);
    const diffBitsA = strips[0].findAll(".bit").filter((bit) => bit.attributes("style")?.includes("rgb(245, 97, 105)"));
    expect(diffBitsA).toHaveLength(3);
    wrapper.unmount();
  });

  it("shows the plain-language verdict ribbon", () => {
    const { a, b } = pair();
    const wrapper = mount(CompareStrip, { props: { a, b } });
    expect(wrapper.find(".verdict-head").text()).toBe("Near-duplicate content — different file, same work.");
    expect(wrapper.find(".verdict-detail").text()).toContain("95%");
    wrapper.unmount();
  });

  it("handles units present on one side only", () => {
    const a = makeSpecimen({ id: "a", explain: makeExplain([makeUnit("meta"), makeUnit("content")]) });
    const b = makeSpecimen({ id: "b", explain: makeExplain([makeUnit("content")]) });
    const wrapper = mount(CompareStrip, { props: { a, b } });
    const metaCard = wrapper.findAll(".diff-card")[0];
    expect(metaCard.find(".dc-pct").text()).toBe("—");
    expect(metaCard.find(".dc-note").text()).toBe("only in A");
    wrapper.unmount();
  });

  it("copies a text report with per-layer lines and the verdict", async () => {
    const { a, b } = pair();
    const wrapper = mount(CompareStrip, { props: { a, b } });
    await wrapper.find(".copy-report").trigger("click");
    await flushPromises();
    const report = vi.mocked(navigator.clipboard.writeText).mock.calls[0][0];
    expect(report).toContain("A: original.jpg");
    expect(report).toContain("CONTENT: 95%");
    expect(report).toContain("Verdict: Near-duplicate content");
    expect(wrapper.find(".copy-report").text()).toBe("Copied!");
    wrapper.unmount();
  });
});
