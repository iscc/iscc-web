/** Integration tests for the App orchestrator: education morph, intake flows, compare. */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import App from "../App.vue";
import EducationStrip from "../components/EducationStrip.vue";
import IntakeCard from "../components/IntakeCard.vue";
import ResultCard from "../components/ResultCard.vue";
import { apiService } from "../services/api.service";
import { fourUnits, makeExplain, makeMetadata } from "./fixtures";

vi.mock("../services/api.service", () => ({
  apiService: {
    isccEndpoint: vi.fn(() => "/api/v1/iscc?semantic=false&granular=false"),
    createIsccFromText: vi.fn(),
    explainIscc: vi.fn(),
    embedMetadata: vi.fn(),
    deleteMedia: vi.fn(async () => undefined),
    downloadUrl: (mediaId: string) => `/api/v1/media/${mediaId}`,
  },
}));

const hljsStub = { template: "<pre class='hljs-stub'>{{ code }}</pre>", props: ["language", "code"] };

const mountApp = () => mount(App, { global: { stubs: { highlightjs: hljsStub } } });

beforeEach(() => {
  vi.mocked(apiService.createIsccFromText).mockResolvedValue(makeMetadata());
  vi.mocked(apiService.explainIscc).mockResolvedValue(makeExplain(fourUnits()));
});

describe("App", () => {
  it("morphs the education strip into the readout feed on the first result", async () => {
    const wrapper = mountApp();
    expect(wrapper.findComponent(EducationStrip).exists()).toBe(true);

    wrapper.findComponent(IntakeCard).vm.$emit("text-submit", "hello world", { semantic: false, granular: true });
    await flushPromises();

    expect(wrapper.findComponent(EducationStrip).exists()).toBe(false);
    const card = wrapper.findComponent(ResultCard);
    expect(card.exists()).toBe(true);
    expect(card.find(".status-pill").text()).toContain("DONE IN");
    expect(apiService.createIsccFromText).toHaveBeenCalledWith("hello world", false, true);
    wrapper.unmount();
  });

  it("decodes a pasted ISCC without uploading", async () => {
    const wrapper = mountApp();
    wrapper.findComponent(IntakeCard).vm.$emit("code-submit", "ISCC:KACYPXW445FTYNJ3");
    await flushPromises();

    expect(apiService.explainIscc).toHaveBeenCalledWith("ISCC:KACYPXW445FTYNJ3");
    const card = wrapper.findComponent(ResultCard);
    expect(card.props("specimen").kind).toBe("code");
    expect(card.find(".status-pill").text()).toContain("DECODED");
    wrapper.unmount();
  });

  it("turns API failures into an error card", async () => {
    vi.mocked(apiService.explainIscc).mockRejectedValue(new Error("400: bad code"));
    const wrapper = mountApp();
    wrapper.findComponent(IntakeCard).vm.$emit("code-submit", "ISCC:KACYPXW445FTYNJ3");
    await flushPromises();

    expect(wrapper.findComponent(ResultCard).find(".alert-strip").text()).toContain("400: bad code");
    wrapper.unmount();
  });

  it("clears stale result cards when the active input mode changes", async () => {
    vi.mocked(apiService.explainIscc).mockRejectedValue(new Error("400: bad code"));
    const wrapper = mountApp();
    const intake = wrapper.findComponent(IntakeCard);

    intake.vm.$emit("code-submit", "ISCC:KACYPXW445FTYNJ3");
    await flushPromises();
    expect(wrapper.findComponent(ResultCard).find(".alert-strip").text()).toContain("400: bad code");

    intake.vm.$emit("mode-change", "text");
    await flushPromises();
    expect(wrapper.findComponent(ResultCard).exists()).toBe(false);
    expect(wrapper.findComponent(EducationStrip).exists()).toBe(true);
    wrapper.unmount();
  });

  it("docks a second specimen for comparison and ejects it again", async () => {
    const wrapper = mountApp();
    const intake = wrapper.findComponent(IntakeCard);
    intake.vm.$emit("text-submit", "first", { semantic: false, granular: false });
    await flushPromises();
    intake.vm.$emit("text-submit", "second", { semantic: false, granular: false });
    await flushPromises();

    const cards = wrapper.findAllComponents(ResultCard);
    expect(cards).toHaveLength(2);
    expect(cards[0].props("compareOptions")).toHaveLength(1);

    cards[0].vm.$emit("compare", cards[1].props("specimen").id);
    await flushPromises();
    expect(wrapper.find(".compare-head").exists()).toBe(true);
    expect(wrapper.find(".verdict-head").text()).toBe("Identical files.");

    wrapper.findComponent(ResultCard).vm.$emit("eject");
    await flushPromises();
    expect(wrapper.find(".compare-head").exists()).toBe(false);
    wrapper.unmount();
  });

  it("re-decodes after embedding metadata and offers the updated file", async () => {
    const updated = makeMetadata({ media_id: "061new1234567", name: "A title" });
    vi.mocked(apiService.embedMetadata).mockResolvedValue(updated);

    const wrapper = mountApp();
    wrapper.findComponent(IntakeCard).vm.$emit("text-submit", "first", { semantic: false, granular: false });
    await flushPromises();

    const card = wrapper.findComponent(ResultCard);
    card.vm.$emit("embed", { name: "A title", description: "" });
    await flushPromises();

    expect(apiService.embedMetadata).toHaveBeenCalledWith("061kcmrj55fi8", { name: "A title", description: "" });
    expect(card.props("specimen").metadata?.media_id).toBe("061new1234567");
    expect(card.props("specimen").metadataChanged).toBe(true);
    wrapper.unmount();
  });

  it("removes a card, deletes the upload and restores the education strip", async () => {
    const wrapper = mountApp();
    wrapper.findComponent(IntakeCard).vm.$emit("text-submit", "first", { semantic: false, granular: false });
    await flushPromises();

    wrapper.findComponent(ResultCard).vm.$emit("remove");
    await flushPromises();

    expect(apiService.deleteMedia).toHaveBeenCalledWith("061kcmrj55fi8");
    expect(wrapper.findComponent(ResultCard).exists()).toBe(false);
    expect(wrapper.findComponent(EducationStrip).exists()).toBe(true);
    wrapper.unmount();
  });
});
