/** Tests for the backend-injected runtime config accessor and derived labels. */
import { afterEach, describe, expect, it } from "vitest";
import { expiryLabel, formatDuration, runtimeConfig } from "../lib/config";

const win = globalThis as typeof globalThis & {
  __ISCC_WEB__?: { semanticDefault?: boolean; storageExpiry?: number };
};

afterEach(() => {
  delete win.__ISCC_WEB__;
});

describe("runtimeConfig", () => {
  it("falls back to built-in defaults when nothing is injected", () => {
    expect(runtimeConfig()).toEqual({ semanticDefault: true, storageExpiry: 3600 });
  });

  it("reads the semantic default from injected backend config", () => {
    win.__ISCC_WEB__ = { semanticDefault: false };
    expect(runtimeConfig().semanticDefault).toBe(false);
  });

  it("reads the storage expiry from injected backend config", () => {
    win.__ISCC_WEB__ = { storageExpiry: 1800 };
    expect(runtimeConfig().storageExpiry).toBe(1800);
  });

  it("merges partial injected config over the fallbacks", () => {
    win.__ISCC_WEB__ = {};
    expect(runtimeConfig()).toEqual({ semanticDefault: true, storageExpiry: 3600 });
  });
});

describe("formatDuration", () => {
  it("renders a single hour as words", () => {
    expect(formatDuration(3600)).toBe("one hour");
  });

  it("pluralizes whole hours", () => {
    expect(formatDuration(7200)).toBe("2 hours");
  });

  it("falls back to minutes when not a whole number of hours", () => {
    expect(formatDuration(1800)).toBe("30 minutes");
    expect(formatDuration(60)).toBe("one minute");
  });

  it("falls back to seconds for sub-minute or odd durations", () => {
    expect(formatDuration(45)).toBe("45 seconds");
    expect(formatDuration(90)).toBe("90 seconds");
  });
});

describe("expiryLabel", () => {
  it("labels the injected expiry window", () => {
    win.__ISCC_WEB__ = { storageExpiry: 1800 };
    expect(expiryLabel()).toBe("30 minutes");
  });

  it("labels the default expiry window", () => {
    expect(expiryLabel()).toBe("one hour");
  });
});
