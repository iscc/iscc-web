/** Per-layer explanation copy for the decoder readout detail panel. */
import type { UnitKind } from "./iscc";

export interface UnitCopy {
  title: string;
  body: string;
  tip: string;
}

const CONTENT_SOURCE: Record<string, string> = {
  text: "perceptual features of the extracted text",
  image: "perceptual features of the decoded image",
  audio: "an audio fingerprint of the decoded waveform",
  video: "perceptual features of the decoded video frames",
  mixed: "perceptual features of the decoded content",
};

/** Explanation copy for one ISCC-UNIT layer, content-aware via the perceptual mode. */
export function unitCopy(kind: UnitKind, mode: string | null | undefined): UnitCopy {
  switch (kind) {
    case "meta":
      return {
        title: "Meta-Code — what the file says about itself",
        body:
          "A similarity hash over the embedded title and description — the metadata, not the content. " +
          "Renaming the file changes nothing; editing its embedded title moves these bits. " +
          "Two files with close Meta-Codes claim to be the same thing.",
        tip:
          "Add a title and description — the service writes them into a copy of your file " +
          "and re-decodes it. Watch how only the META field changes.",
      };
    case "semantic":
      return {
        title: "Semantic-Code — what the work means",
        body:
          "Derived from ML embeddings of meaning — not wording or pixels. A translation or a careful " +
          "paraphrase keeps these bits close while the Content-Code drifts apart. Slower to compute and " +
          "not part of plain ISO 24138 — which is why it ships behind the experimental toggle.",
        tip: "Drop a paraphrased or translated copy of the same work and compare: Semantic stays close while Content moves.",
      };
    case "content":
      return {
        title: "Content-Code — what the work looks like",
        body:
          `Derived from ${CONTENT_SOURCE[mode ?? "mixed"] ?? CONTENT_SOURCE.mixed} — not the bytes. ` +
          "Re-encoding, format conversion or light edits barely move these bits. " +
          "Two files with a small Hamming distance here show the same work.",
        tip: "Drop a re-encoded or lightly edited copy of this file and compare the two results — watch how few CONTENT bits flip.",
      };
    case "data":
      return {
        title: "Data-Code — how the file is stored",
        body:
          "A similarity hash over the raw bitstream, independent of media type. It tracks storage, " +
          "not meaning: the same content saved in another format diverges here while Content holds. " +
          "Robust against small inserts and deletes.",
        tip: "Save the same content in another format and drop both files: Data diverges while Content holds — storage and work, separated.",
      };
    case "instance":
      return {
        title: "Instance-Code — the exact bytes",
        body:
          "A cryptographic checksum of the file as-is. One flipped bit anywhere changes it completely — " +
          "there is no “similar” on this layer, only identical or not. " +
          "This is the integrity check: byte-for-byte identity.",
        tip: "Change a single byte — one pixel, one character — and drop the file again: this checksum flips entirely while Content barely moves.",
      };
  }
}
