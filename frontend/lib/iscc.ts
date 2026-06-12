/** Pure helpers for parsing, comparing and presenting ISCC codes and units. */

export type UnitKind = "meta" | "semantic" | "content" | "data" | "instance";

export const UNIT_ORDER: UnitKind[] = ["meta", "semantic", "content", "data", "instance"];

/**
 * Visual identity of each ISCC-UNIT layer (Concept 4 decoder readout palette;
 * mirrored as --iscc-unit-* custom properties in main.scss).
 */
export const UNIT_STYLE: Record<
  UnitKind,
  { label: string; color: string; accent: string; tint: string; meaning: string }
> = {
  meta: {
    label: "META",
    color: "#7ac2f7",
    accent: "#1f86c9",
    tint: "rgba(122, 194, 247, 0.18)",
    meaning: "metadata similarity",
  },
  semantic: {
    label: "SEMANTIC",
    color: "#4596f5",
    accent: "#2e7ad6",
    tint: "rgba(69, 150, 245, 0.13)",
    meaning: "semantic similarity · experimental",
  },
  content: {
    label: "CONTENT",
    color: "#0054b2",
    accent: "#0054b2",
    tint: "rgba(0, 84, 178, 0.10)",
    meaning: "syntactic similarity",
  },
  data: {
    label: "DATA",
    color: "#123663",
    accent: "#123663",
    tint: "rgba(18, 54, 99, 0.10)",
    meaning: "data similarity",
  },
  instance: {
    label: "INSTANCE",
    color: "#a6db50",
    accent: "#6d9c2a",
    tint: "rgba(166, 219, 80, 0.18)",
    meaning: "exact match · checksum",
  },
};

const BASE32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

/** MainType of an ISCC-UNIT read from its codec header (top 4 bits of the first base32 char). */
export function unitKindFromIscc(unit: string): UnitKind | null {
  const first = unit
    .replace(/^ISCC:/i, "")
    .charAt(0)
    .toUpperCase();
  if (!first) return null;
  const value = BASE32.indexOf(first);
  if (value < 0) return null;
  return UNIT_ORDER[value >> 1] ?? null;
}

/** Type prefix of a readable unit name: "META-NONE-V0-64-c8a70639…" -> "META-NONE-V0-64". */
export function unitTypeLabel(readable: string): string {
  return readable.split("-").slice(0, 4).join("-");
}

/** SubType segment of a readable unit name: "CONTENT-IMAGE-V0-64-…" -> "IMAGE". */
export function unitSubtype(readable: string): string {
  return readable.split("-")[1] ?? "";
}

/** Percentage of equal bits between two equal-length bit strings, or null when not comparable. */
export function matchPercent(aBits: string, bBits: string): number | null {
  if (!aBits || !bBits || aBits.length !== bBits.length) return null;
  let equal = 0;
  for (let i = 0; i < aBits.length; i++) {
    if (aBits[i] === bBits[i]) equal++;
  }
  return Math.round((equal / aBits.length) * 100);
}

/** Traffic-light color for a similarity percentage. */
export function pctColor(pct: number): string {
  return pct >= 80 ? "#a6db50" : pct >= 55 ? "#ffc300" : "#f56169";
}

export const ISCC_PATTERN = /^ISCC:[A-Z2-7]{10,73}$/;

/** Canonical form of a user-entered ISCC (trimmed, uppercased, prefixed) or null if invalid. */
export function normalizeIscc(input: string): string | null {
  let code = input.trim().toUpperCase();
  if (!code) return null;
  if (!code.startsWith("ISCC:")) code = `ISCC:${code}`;
  return ISCC_PATTERN.test(code) ? code : null;
}

/** Human-readable byte count: 53256 -> "52.0 KB". */
export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  let value = bytes;
  let unit = "B";
  for (const next of ["KB", "MB", "GB", "TB"]) {
    if (value < 1024) break;
    value /= 1024;
    unit = next;
  }
  return `${value >= 100 ? value.toFixed(0) : value.toFixed(value >= 10 ? 1 : 2)} ${unit}`;
}

/** Deterministic pseudo-random base32 string driving the decode animation. */
export function scramble(length: number, seed: number): string {
  let state = (seed * 2654435761 + 1013904223) >>> 0;
  let out = "";
  for (let i = 0; i < length; i++) {
    state = (state * 1103515245 + 12345) >>> 0;
    out += BASE32[(state >>> 16) % 32];
  }
  return out;
}

/** Deterministic '0'/'1' noise pattern (per-unit bit texture while hashing). */
export function seedBits(seed: string, length = 64): string {
  let state = 0;
  for (let i = 0; i < seed.length; i++) {
    state = (state * 31 + seed.charCodeAt(i)) >>> 0;
  }
  let out = "";
  for (let i = 0; i < length; i++) {
    state = (state * 1103515245 + 12345) >>> 0;
    out += (state >>> 16) & 1 ? "1" : "0";
  }
  return out;
}

export interface UnitDiff {
  kind: UnitKind;
  a: Api.IsccUnit | null;
  b: Api.IsccUnit | null;
  /** Match percentage, or null when a side is missing or the units are not comparable. */
  pct: number | null;
  /** One-line human reading of this layer's diff. */
  note: string;
}

/** Per-layer one-liner for a comparison result. */
export function unitDiffNote(kind: UnitKind, pct: number): string {
  switch (kind) {
    case "meta":
      return pct >= 95
        ? "embedded metadata matches"
        : pct >= 60
          ? "metadata partially matches"
          : "embedded metadata diverges";
    case "semantic":
      return pct >= 90 ? "same meaning despite different wording" : pct >= 70 ? "related meaning" : "meaning diverges";
    case "content":
      return pct >= 95
        ? "same work — survives re-encoding"
        : pct >= 80
          ? "same work with minor edits"
          : pct >= 60
            ? "substantially edited"
            : "different works";
    case "data":
      return pct >= 90
        ? "near-identical bitstream"
        : pct >= 70
          ? "partially shared data"
          : "bitstream reshaped (format/compression)";
    case "instance":
      return pct === 100 ? "byte-for-byte identical" : "different files — no byte identity";
  }
}

/** Pair up the units of two decomposed ISCCs layer by layer in axis order. */
export function compareUnits(aUnits: Api.IsccUnit[], bUnits: Api.IsccUnit[]): UnitDiff[] {
  const byKind = (units: Api.IsccUnit[]) => {
    const map = new Map<UnitKind, Api.IsccUnit>();
    for (const unit of units) {
      const kind = unitKindFromIscc(unit.iscc_unit);
      if (kind && !map.has(kind)) map.set(kind, unit);
    }
    return map;
  };
  const a = byKind(aUnits);
  const b = byKind(bUnits);
  const diffs: UnitDiff[] = [];
  for (const kind of UNIT_ORDER) {
    const ua = a.get(kind) ?? null;
    const ub = b.get(kind) ?? null;
    if (!ua && !ub) continue;
    let pct: number | null = null;
    let note: string;
    if (!ua || !ub) {
      note = `only in ${ua ? "A" : "B"}`;
    } else if ((kind === "content" || kind === "semantic") && unitSubtype(ua.readable) !== unitSubtype(ub.readable)) {
      note = "different media types — not comparable";
    } else {
      pct = matchPercent(ua.hash_bits, ub.hash_bits);
      note = pct === null ? "different unit lengths — not comparable" : unitDiffNote(kind, pct);
    }
    diffs.push({ kind, a: ua, b: ub, pct, note });
  }
  return diffs;
}

export interface CompareVerdict {
  headline: string;
  detail: string;
}

/** Plain-language verdict derived from per-layer match percentages. */
export function verdict(diffs: UnitDiff[]): CompareVerdict {
  const pct = (kind: UnitKind) => diffs.find((d) => d.kind === kind)?.pct ?? null;
  const instance = pct("instance");
  const content = pct("content");
  const semantic = pct("semantic");
  const data = pct("data");
  const meta = pct("meta");

  if (instance === 100) {
    return {
      headline: "Identical files.",
      detail: "The Instance-Codes match exactly — these are byte-for-byte the same file.",
    };
  }
  if (content !== null && content >= 95) {
    const metaNote = meta !== null && meta < 60 ? " while embedded metadata diverges" : "";
    return {
      headline: "Near-duplicate content — different file, same work.",
      detail: `The content survives re-encoding (${content}% match)${metaNote} — only the exact bytes differ.`,
    };
  }
  if (content !== null && content >= 80) {
    return {
      headline: "Closely related content — likely an edited copy.",
      detail: `The Content-Codes match ${content}% — the same work with light edits or processing.`,
    };
  }
  if (semantic !== null && semantic >= 80) {
    return {
      headline: "Semantically similar — same meaning, different expression.",
      detail: `The Semantic-Codes match ${semantic}% while the syntactic content diverges — e.g. a paraphrase or translation.`,
    };
  }
  if (content !== null && content >= 60) {
    return {
      headline: "Related content with substantial edits.",
      detail: `The Content-Codes match ${content}% — noticeably edited, but probably derived from the same work.`,
    };
  }
  if (data !== null && data >= 80) {
    return {
      headline: "Shared data without matching content.",
      detail: `The raw bitstreams overlap (${data}% Data-Code match) although the decoded content differs.`,
    };
  }
  if (!diffs.some((d) => d.pct !== null)) {
    return {
      headline: "Not directly comparable.",
      detail: "No layer has matching unit types and lengths in both codes.",
    };
  }
  return {
    headline: "No meaningful similarity.",
    detail: "These two differ on every comparable layer.",
  };
}
