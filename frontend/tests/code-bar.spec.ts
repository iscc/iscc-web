/** Tests for the ISCC-CODE bar: empty slot, static code and the landing reveal. */
import { afterEach, describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import CodeBar from "../components/CodeBar.vue";
import { SAMPLE_ISCC } from "./fixtures";

/** Give jsdom the Web Animations entry points the reveal needs; the dot is `elapsed` ms into its hop. */
const stubAnimations = (elapsed: number) => {
  const animate = vi.fn();
  Object.defineProperty(HTMLElement.prototype, "animate", { value: animate, configurable: true });
  Object.defineProperty(Element.prototype, "getAnimations", {
    value: () => [{ currentTime: elapsed }],
    configurable: true,
  });
  return animate;
};

afterEach(() => {
  vi.useRealTimers();
  Reflect.deleteProperty(HTMLElement.prototype, "animate");
  Reflect.deleteProperty(Element.prototype, "getAnimations");
});

describe("CodeBar", () => {
  it("shows a known code at once, one span per character", () => {
    const wrapper = mount(CodeBar, { props: { code: SAMPLE_ISCC } });
    expect(wrapper.classes()).toContain("iscc-code-bar");
    expect(wrapper.text()).toBe(SAMPLE_ISCC);
    expect(wrapper.findAll(".glyph")).toHaveLength(SAMPLE_ISCC.length);
    expect(wrapper.find(".spinning, .locked").exists()).toBe(false);
  });

  it("is an empty slot with the coral dot until a code exists", async () => {
    const wrapper = mount(CodeBar, { props: { code: SAMPLE_ISCC } });
    await wrapper.setProps({ code: null });
    expect(wrapper.classes()).toContain("slot");
    expect(wrapper.classes()).not.toContain("iscc-code-bar");
    expect(wrapper.find(".iscc-dot").exists()).toBe(true);
    expect(wrapper.text()).toBe("Your ISCC-CODE will land here");
  });

  it("shows an arriving code straight away where animation is unavailable", async () => {
    const wrapper = mount(CodeBar, { props: { code: null } });
    await wrapper.setProps({ code: SAMPLE_ISCC });
    expect(wrapper.text()).toBe(SAMPLE_ISCC);
    expect(wrapper.find(".spinning").exists()).toBe(false);
  });

  it("lands the dot on its next floor contact, then spins and locks the code into place", async () => {
    vi.useFakeTimers({
      toFake: ["setTimeout", "clearTimeout", "requestAnimationFrame", "cancelAnimationFrame", "performance"],
    });
    const animate = stubAnimations(500);
    const wrapper = mount(CodeBar, { props: { code: null } });
    await wrapper.setProps({ code: SAMPLE_ISCC });

    // 60 ms until the dot touches down (560 ms hop, 500 ms in): still an empty slot.
    await vi.advanceTimersByTimeAsync(50);
    expect(wrapper.find(".iscc-dot").exists()).toBe(true);

    // Touch-down: coral floods in and every character starts spinning.
    await vi.advanceTimersByTimeAsync(30);
    expect(wrapper.classes()).toContain("iscc-code-bar");
    expect(animate).toHaveBeenCalledTimes(2); // flood + bounce
    expect(wrapper.findAll(".glyph")).toHaveLength(SAMPLE_ISCC.length);
    expect(wrapper.find(".visually-hidden").text()).toBe(SAMPLE_ISCC);

    // Mid-reveal: the lock wave has started from the left; the rest still spins.
    await vi.advanceTimersByTimeAsync(400);
    const glyphs = wrapper.findAll(".glyph");
    expect(glyphs[0].classes()).toContain("locked");
    expect(glyphs[glyphs.length - 1].classes()).toContain("spinning");
    expect(glyphs[0].text()).toBe("I");

    // Settled: the plain code, no reveal classes and no screen-reader duplicate.
    await vi.advanceTimersByTimeAsync(2000);
    expect(wrapper.text()).toBe(SAMPLE_ISCC);
    expect(wrapper.find(".spinning, .locked").exists()).toBe(false);
    expect(wrapper.find(".visually-hidden").exists()).toBe(false);
    wrapper.unmount();
  });

  it("skips the reveal for a code that replaces another one", async () => {
    stubAnimations(0);
    const wrapper = mount(CodeBar, { props: { code: SAMPLE_ISCC } });
    await wrapper.setProps({ code: "ISCC:KACYPXW445FTYNJ3" });
    expect(wrapper.text()).toBe("ISCC:KACYPXW445FTYNJ3");
    expect(wrapper.find(".spinning").exists()).toBe(false);
  });
});
