/** Tests for the decoder readout card: lifecycle states, unit selection, compare docking. */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import ResultCard from "../components/ResultCard.vue";
import { SAMPLE_ISCC, makeExplain, makeSpecimen, makeUnit } from "./fixtures";

const hljsStub = { template: "<pre class='hljs-stub'>{{ code }}</pre>", props: ["language", "code"] };

const mountCard = (
  specimen: IsccWeb.Specimen,
  extra: Partial<{
    compareTarget: IsccWeb.Specimen | null;
    compareOptions: Array<{ id: string; label: string; iscc: string }>;
  }> = {},
) =>
  mount(ResultCard, {
    props: { specimen, compareTarget: null, compareOptions: [], ...extra },
    global: { stubs: { highlightjs: hljsStub } },
  });

beforeEach(() => {
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText: vi.fn().mockResolvedValue(undefined) },
    configurable: true,
  });
});

describe("ResultCard — done state", () => {
  it("renders the composite code, unit fields and the elapsed pill", () => {
    const wrapper = mountCard(makeSpecimen());
    expect(wrapper.find(".code-bar").text()).toBe(SAMPLE_ISCC);
    expect(wrapper.findAll(".unit-field")).toHaveLength(4);
    expect(wrapper.find(".status-pill").text()).toContain("DONE IN 1.8 S");
    wrapper.unmount();
  });

  it("selects CONTENT by default and switches the detail panel on click", async () => {
    const wrapper = mountCard(makeSpecimen());
    expect(wrapper.find(".unit-field.selected").text()).toContain("CONTENT");
    expect(wrapper.find(".layer-title").text()).toContain("Content-Code");

    const metaField = wrapper.findAll(".unit-field").find((f) => f.text().includes("META"));
    await metaField!.trigger("click");
    expect(wrapper.find(".layer-title").text()).toContain("Meta-Code");
    // META layer exposes the live embed experiment for file specimens
    expect(wrapper.find("input[placeholder='Title']").exists()).toBe(true);
    wrapper.unmount();
  });

  it("falls back to the first unit for 2-unit wide ISCC-SUM results", () => {
    const wide = makeSpecimen({
      explain: makeExplain([
        makeUnit("data", { bits: "10".repeat(64) }),
        makeUnit("instance", { bits: "01".repeat(64) }),
      ]),
      metadata: null,
    });
    const wrapper = mountCard(wide);
    expect(wrapper.findAll(".unit-field")).toHaveLength(2);
    expect(wrapper.find(".unit-field.selected").text()).toContain("DATA");
    expect(wrapper.find(".unit-field.selected").text()).toContain("128 bit");
    wrapper.unmount();
  });

  it("copies the composite code to the clipboard", async () => {
    const wrapper = mountCard(makeSpecimen());
    await wrapper.find(".copy-btn").trigger("click");
    await flushPromises();
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(SAMPLE_ISCC);
    expect(wrapper.find(".copy-btn").text()).toContain("Copied");
    wrapper.unmount();
  });

  it("discloses the raw result JSON on demand", async () => {
    const wrapper = mountCard(makeSpecimen());
    expect(wrapper.find(".raw-json").exists()).toBe(false);
    await wrapper.find(".raw-toggle").trigger("click");
    expect(wrapper.find(".raw-json").text()).toContain(SAMPLE_ISCC);
    wrapper.unmount();
  });
});

describe("ResultCard — lifecycle states", () => {
  it("shows honest upload numbers and queued unit placeholders", () => {
    const wrapper = mountCard(
      makeSpecimen({
        status: "uploading",
        progress: 42,
        bytesUploaded: 21504,
        bytesTotal: 51200,
        metadata: null,
        explain: null,
        elapsed: null,
      }),
    );
    expect(wrapper.find(".status-pill").text()).toContain("UPLOADING · 42% · 21.0 KB / 50.0 KB");
    expect(wrapper.findAll(".unit-field")).toHaveLength(4);
    expect(wrapper.find(".unit-field").text()).toContain("queued");
    expect(wrapper.find(".copy-btn").attributes("disabled")).toBeDefined();
    wrapper.unmount();
  });

  it("shows the decode animation while processing, five placeholders with semantic on", () => {
    const wrapper = mountCard(
      makeSpecimen({ status: "processing", semantic: true, metadata: null, explain: null, elapsed: null }),
    );
    expect(wrapper.find(".status-pill").text()).toContain("DECODING");
    expect(wrapper.findAll(".unit-field")).toHaveLength(5);
    expect(wrapper.find(".unit-field").text()).toContain("hashing…");
    expect(wrapper.find(".scan-line").exists()).toBe(true);
    wrapper.unmount();
  });

  it("bases the SEMANTIC ON chip on the actual units once settled", () => {
    // embed re-processing has no semantic param and drops the semantic unit -
    // the chip must follow the readout, not the original toggle
    const working = mountCard(
      makeSpecimen({ status: "processing", semantic: true, metadata: null, explain: null, elapsed: null }),
    );
    expect(working.find(".chip-semantic").exists()).toBe(true);
    working.unmount();

    const fourUnitsDone = mountCard(makeSpecimen({ semantic: true }));
    expect(fourUnitsDone.find(".chip-semantic").exists()).toBe(false);
    fourUnitsDone.unmount();

    const withSemanticUnit = mountCard(
      makeSpecimen({
        semantic: true,
        explain: makeExplain([makeUnit("meta"), makeUnit("semantic"), makeUnit("content"), makeUnit("instance")]),
      }),
    );
    expect(withSemanticUnit.find(".chip-semantic").exists()).toBe(true);
    withSemanticUnit.unmount();
  });

  it("shows the error strip with the failure message", () => {
    const wrapper = mountCard(
      makeSpecimen({ status: "error", error: "422: unsupported", metadata: null, explain: null }),
    );
    expect(wrapper.find(".alert-strip").text()).toContain("422: unsupported");
    expect(wrapper.find(".navy-strip").exists()).toBe(false);
    wrapper.unmount();
  });
});

describe("ResultCard — code specimens", () => {
  it("hides file-specific panels and shows the code structure", () => {
    const specimen = makeSpecimen({ kind: "code", label: "Decoded ISCC", metadata: null, elapsed: null });
    const wrapper = mountCard(specimen);
    expect(wrapper.find(".status-pill").text()).toContain("DECODED");
    expect(wrapper.text()).toContain("ISCC-IMAGE-V0-MCDI · 4 units");
    expect(wrapper.find(".panel-label").text()).not.toContain("Specimen preview");
    expect(wrapper.text()).toContain("Code structure");
    expect(wrapper.find("a[title='Download file']").exists()).toBe(false);
    wrapper.unmount();
  });
});

describe("ResultCard — comparison", () => {
  it("docks directly when exactly one other specimen exists", async () => {
    const wrapper = mountCard(makeSpecimen(), {
      compareOptions: [{ id: "other-1", label: "other.jpg", iscc: SAMPLE_ISCC }],
    });
    await wrapper.find(".compare-btn").trigger("click");
    expect(wrapper.emitted("compare")).toEqual([["other-1"]]);
    wrapper.unmount();
  });

  it("opens a picker when several candidates exist", async () => {
    const wrapper = mountCard(makeSpecimen(), {
      compareOptions: [
        { id: "other-1", label: "one.jpg", iscc: SAMPLE_ISCC },
        { id: "other-2", label: "two.jpg", iscc: SAMPLE_ISCC },
      ],
    });
    await wrapper.find(".compare-btn").trigger("click");
    expect(wrapper.emitted("compare")).toBeUndefined();
    const picks = wrapper.findAll(".pick");
    expect(picks).toHaveLength(2);
    await picks[1].trigger("click");
    expect(wrapper.emitted("compare")).toEqual([["other-2"]]);
    wrapper.unmount();
  });

  it("renders the diff mode with swap and eject", async () => {
    const target = makeSpecimen({ id: "spec-2", label: "copy.jpg" });
    const wrapper = mountCard(makeSpecimen({ compareWithId: "spec-2" }), { compareTarget: target });

    expect(wrapper.find(".compare-head").exists()).toBe(true);
    expect(wrapper.find(".verdict-ribbon").exists()).toBe(true);
    expect(wrapper.find(".compare-legend").text()).toContain("bit equal in A and B");

    const buttons = wrapper.findAll(".ghost-btn");
    await buttons[0].trigger("click");
    expect(wrapper.emitted("swap")).toHaveLength(1);
    await buttons[1].trigger("click");
    expect(wrapper.emitted("eject")).toHaveLength(1);
    wrapper.unmount();
  });
});
