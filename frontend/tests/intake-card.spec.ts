/** Tests for the intake instrument: tabs, toggles, validation and drop catcher. */
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import IntakeCard from "../components/IntakeCard.vue";

const tabButton = (wrapper: ReturnType<typeof mount>, label: string) => {
  const button = wrapper.findAll("button.intake-tab").find((b) => b.text().includes(label));
  if (!button) throw new Error(`tab ${label} not found`);
  return button;
};

const dragEvent = (type: string, files: File[] = []) => {
  const event = new Event(type, { bubbles: true, cancelable: true }) as Event & {
    dataTransfer: { types: string[]; files: File[] };
  };
  event.dataTransfer = { types: ["Files"], files };
  return event;
};

describe("IntakeCard", () => {
  it("shows the drop zone and toggles on the file tab by default", () => {
    const wrapper = mount(IntakeCard);
    expect(wrapper.find(".drop-zone").exists()).toBe(true);
    expect(wrapper.find("#semantic-toggle").exists()).toBe(true);
    expect(wrapper.find("#granular-toggle").exists()).toBe(true);
    wrapper.unmount();
  });

  it("generates from plain text with the current toggle state", async () => {
    const wrapper = mount(IntakeCard);
    await tabButton(wrapper, "Plain text").trigger("click");

    const button = wrapper.find("button.btn-go");
    expect(button.attributes("disabled")).toBeDefined();

    await wrapper.find("textarea.text-input").setValue("hello iscc");
    await wrapper.find("#semantic-toggle").setValue(true);
    expect(button.attributes("disabled")).toBeUndefined();
    await button.trigger("click");

    expect(wrapper.emitted("text-submit")).toEqual([["hello iscc", { semantic: true, granular: false }]]);
    wrapper.unmount();
  });

  it("validates and normalizes ISCC input on the code tab", async () => {
    const wrapper = mount(IntakeCard);
    await tabButton(wrapper, "ISCC code").trigger("click");

    // generation toggles do not apply to decoding
    expect(wrapper.find("#semantic-toggle").exists()).toBe(false);

    const input = wrapper.find("input.code-input");
    const button = wrapper.find("button.btn-go");

    await input.setValue("definitely not an iscc!");
    expect(wrapper.find(".valid-dot").classes()).toContain("invalid");
    expect(button.attributes("disabled")).toBeDefined();

    await input.setValue("kacypxw445ftynj3cysxhafjma2hu");
    expect(wrapper.find(".valid-dot").classes()).toContain("valid");
    await button.trigger("click");

    expect(wrapper.emitted("code-submit")).toEqual([["ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HU"]]);
    wrapper.unmount();
  });

  it("emits file-added with the toggle state when files are added", async () => {
    const wrapper = mount(IntakeCard);
    await wrapper.find("#granular-toggle").setValue(true);

    const file = new File(["payload"], "sample.txt", { type: "text/plain" });
    window.dispatchEvent(dragEvent("drop", [file]));
    await wrapper.vm.$nextTick();

    const emitted = wrapper.emitted("file-added");
    expect(emitted).toHaveLength(1);
    const [uppyFile, options] = emitted![0] as [{ name: string }, { semantic: boolean; granular: boolean }];
    expect(uppyFile.name).toBe("sample.txt");
    expect(options).toMatchObject({ semantic: false, granular: true });
    wrapper.unmount();
  });

  it("accepts the same file twice (compare-an-edited-copy flow)", async () => {
    const wrapper = mount(IntakeCard);
    const file = new File(["payload"], "sample.txt", { type: "text/plain" });
    window.dispatchEvent(dragEvent("drop", [file]));
    window.dispatchEvent(dragEvent("drop", [file]));
    await wrapper.vm.$nextTick();

    const emitted = wrapper.emitted("file-added");
    expect(emitted).toHaveLength(2);
    const ids = emitted!.map((args) => (args[0] as { id: string }).id);
    expect(new Set(ids).size).toBe(2);
    wrapper.unmount();
  });

  it("shows the page-wide drop catcher while dragging files", async () => {
    const wrapper = mount(IntakeCard);
    expect(wrapper.find(".drop-catcher").exists()).toBe(false);

    window.dispatchEvent(dragEvent("dragenter"));
    await wrapper.vm.$nextTick();
    expect(wrapper.find(".drop-catcher").exists()).toBe(true);

    window.dispatchEvent(dragEvent("dragleave"));
    await wrapper.vm.$nextTick();
    expect(wrapper.find(".drop-catcher").exists()).toBe(false);
    wrapper.unmount();
  });
});
