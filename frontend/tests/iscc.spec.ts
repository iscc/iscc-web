/** Tests for the pure ISCC helpers in lib/iscc.ts. */
import { describe, expect, it } from "vitest";
import {
  type UnitDiff,
  type UnitKind,
  compareUnits,
  formatBytes,
  matchPercent,
  normalizeIscc,
  pctColor,
  scramble,
  seedBits,
  unitDiffNote,
  unitKindFromIscc,
  unitSubtype,
  unitTypeLabel,
  verdict,
} from "../lib/iscc";
import { makeUnit } from "./fixtures";

describe("unitKindFromIscc", () => {
  it("maps the codec header to the unit maintype", () => {
    expect(unitKindFromIscc("ISCC:AAAWN77F73NA44D7")).toBe("meta");
    expect(unitKindFromIscc("CAA7GZ4J3DQT2HKW")).toBe("semantic");
    expect(unitKindFromIscc("ISCC:EAACYSXHAFJMA2HU")).toBe("content");
    expect(unitKindFromIscc("iscc:gaaunrfe3blhrscx")).toBe("data");
    expect(unitKindFromIscc("ISCC:IAAM5AEGQY5JLZLX")).toBe("instance");
  });

  it("returns null for composite codes and invalid input", () => {
    expect(unitKindFromIscc("ISCC:KACYPXW445FTYNJ3")).toBeNull();
    expect(unitKindFromIscc("")).toBeNull();
    expect(unitKindFromIscc("ISCC:0000")).toBeNull();
  });
});

describe("unitTypeLabel / unitSubtype", () => {
  it("extracts the type prefix and subtype", () => {
    expect(unitTypeLabel("META-NONE-V0-64-c8a70639eb1167b3")).toBe("META-NONE-V0-64");
    expect(unitSubtype("CONTENT-IMAGE-V0-64-2b8e11c6f04a55d3")).toBe("IMAGE");
    expect(unitSubtype("")).toBe("");
  });
});

describe("matchPercent", () => {
  it("computes the percentage of equal bits", () => {
    expect(matchPercent("1111", "1111")).toBe(100);
    expect(matchPercent("1111", "0000")).toBe(0);
    expect(matchPercent("1100", "1111")).toBe(50);
  });

  it("returns null for unequal lengths or empty input", () => {
    expect(matchPercent("11", "111")).toBeNull();
    expect(matchPercent("", "")).toBeNull();
  });
});

describe("pctColor", () => {
  it("maps percentages to traffic-light colors", () => {
    expect(pctColor(100)).toBe("#a6db50");
    expect(pctColor(80)).toBe("#a6db50");
    expect(pctColor(79)).toBe("#ffc300");
    expect(pctColor(55)).toBe("#ffc300");
    expect(pctColor(54)).toBe("#f56169");
  });
});

describe("normalizeIscc", () => {
  it("canonicalizes valid input", () => {
    expect(normalizeIscc("ISCC:KACYPXW445FTYNJ3")).toBe("ISCC:KACYPXW445FTYNJ3");
    expect(normalizeIscc("kacypxw445ftynj3")).toBe("ISCC:KACYPXW445FTYNJ3");
    expect(normalizeIscc("  iscc:kacypxw445ftynj3  ")).toBe("ISCC:KACYPXW445FTYNJ3");
  });

  it("rejects invalid input", () => {
    expect(normalizeIscc("")).toBeNull();
    expect(normalizeIscc("not an iscc")).toBeNull();
    expect(normalizeIscc("ISCC:ABC")).toBeNull(); // too short
    expect(normalizeIscc("ISCC:" + "A".repeat(74))).toBeNull(); // too long
    expect(normalizeIscc("ISCC:KACY01")).toBeNull(); // 0 and 1 are not base32
  });
});

describe("formatBytes", () => {
  it("formats byte counts human-readably", () => {
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(1024)).toBe("1.00 KB");
    expect(formatBytes(53256)).toBe("52.0 KB");
    expect(formatBytes(2979658)).toBe("2.84 MB");
    expect(formatBytes(-1)).toBe("");
  });
});

describe("scramble / seedBits", () => {
  it("is deterministic per seed and uses the base32 alphabet", () => {
    expect(scramble(16, 7)).toBe(scramble(16, 7));
    expect(scramble(16, 7)).not.toBe(scramble(16, 8));
    expect(scramble(64, 3)).toMatch(/^[A-Z2-7]{64}$/);
  });

  it("produces deterministic bit noise", () => {
    expect(seedBits("noise-meta")).toBe(seedBits("noise-meta"));
    expect(seedBits("noise-meta")).toHaveLength(64);
    expect(seedBits("noise-meta", 128)).toMatch(/^[01]{128}$/);
    expect(seedBits("noise-meta")).not.toBe(seedBits("noise-data"));
  });
});

describe("compareUnits", () => {
  it("pairs units by layer in axis order", () => {
    const a = [makeUnit("instance"), makeUnit("meta"), makeUnit("content")];
    const b = [makeUnit("meta"), makeUnit("content"), makeUnit("instance")];
    const diffs = compareUnits(a, b);
    expect(diffs.map((d) => d.kind)).toEqual(["meta", "content", "instance"]);
    expect(diffs.every((d) => d.pct === 100)).toBe(true);
  });

  it("flags units present on one side only", () => {
    const diffs = compareUnits([makeUnit("meta"), makeUnit("content")], [makeUnit("content")]);
    const meta = diffs.find((d) => d.kind === "meta");
    expect(meta?.pct).toBeNull();
    expect(meta?.note).toBe("only in A");
  });

  it("refuses to compare content units of different media types", () => {
    const diffs = compareUnits([makeUnit("content", { subtype: "IMAGE" })], [makeUnit("content", { subtype: "TEXT" })]);
    expect(diffs[0].pct).toBeNull();
    expect(diffs[0].note).toBe("different media types — not comparable");
  });

  it("refuses to compare units of different bit lengths", () => {
    const diffs = compareUnits(
      [makeUnit("data", { bits: "10".repeat(32) })],
      [makeUnit("data", { bits: "10".repeat(64) })],
    );
    expect(diffs[0].pct).toBeNull();
    expect(diffs[0].note).toBe("different unit lengths — not comparable");
  });

  it("computes the match percentage for comparable units", () => {
    const bitsA = "1".repeat(64);
    const bitsB = "0".repeat(3) + "1".repeat(61);
    const diffs = compareUnits([makeUnit("content", { bits: bitsA })], [makeUnit("content", { bits: bitsB })]);
    expect(diffs[0].pct).toBe(95);
    expect(diffs[0].note).toBe("same work — survives re-encoding");
  });
});

describe("unitDiffNote", () => {
  it("describes each layer's diff in plain language", () => {
    expect(unitDiffNote("instance", 100)).toBe("byte-for-byte identical");
    expect(unitDiffNote("instance", 99)).toBe("different files — no byte identity");
    expect(unitDiffNote("content", 80)).toBe("same work with minor edits");
    expect(unitDiffNote("meta", 30)).toBe("embedded metadata diverges");
    expect(unitDiffNote("semantic", 95)).toBe("same meaning despite different wording");
    expect(unitDiffNote("data", 95)).toBe("near-identical bitstream");
  });
});

describe("verdict", () => {
  const diff = (kind: UnitKind, pct: number | null): UnitDiff => ({ kind, a: null, b: null, pct, note: "" });

  it("detects identical files", () => {
    const v = verdict([diff("content", 100), diff("instance", 100)]);
    expect(v.headline).toBe("Identical files.");
  });

  it("detects near-duplicate content with diverging metadata", () => {
    const v = verdict([diff("meta", 50), diff("content", 95), diff("data", 70), diff("instance", 48)]);
    expect(v.headline).toBe("Near-duplicate content — different file, same work.");
    expect(v.detail).toContain("95%");
    expect(v.detail).toContain("metadata diverges");
  });

  it("detects edited copies", () => {
    const v = verdict([diff("content", 85), diff("instance", 50)]);
    expect(v.headline).toBe("Closely related content — likely an edited copy.");
  });

  it("detects semantic-only similarity", () => {
    const v = verdict([diff("semantic", 90), diff("content", 55), diff("instance", 50)]);
    expect(v.headline).toBe("Semantically similar — same meaning, different expression.");
  });

  it("detects substantial edits", () => {
    const v = verdict([diff("content", 65), diff("instance", 50)]);
    expect(v.headline).toBe("Related content with substantial edits.");
  });

  it("detects shared data without matching content", () => {
    const v = verdict([diff("content", 40), diff("data", 85), diff("instance", 50)]);
    expect(v.headline).toBe("Shared data without matching content.");
  });

  it("reports dissimilarity and non-comparability", () => {
    expect(verdict([diff("content", 50), diff("instance", 49)]).headline).toBe("No meaningful similarity.");
    expect(verdict([diff("content", null), diff("data", null)]).headline).toBe("Not directly comparable.");
    expect(verdict([]).headline).toBe("Not directly comparable.");
  });
});
