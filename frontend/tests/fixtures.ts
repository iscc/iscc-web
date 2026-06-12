/** Deterministic ISCC fixtures (units, metadata, specimens) for component tests. */
import { type UnitKind, seedBits } from "../lib/iscc";

const HEAD: Record<UnitKind, string> = {
  meta: "AAA",
  semantic: "CAA",
  content: "EAA",
  data: "GAA",
  instance: "IAA",
};

const READABLE: Record<UnitKind, string> = {
  meta: "META",
  semantic: "SEMANTIC",
  content: "CONTENT",
  data: "DATA",
  instance: "INSTANCE",
};

export const SAMPLE_ISCC = "ISCC:KECWN77F73NA44D7BNDLJCRJ3M2YQGCKSDIQUJZJ74GQRTAYPHE5NVB3SQXWBHJM";

export function makeUnit(
  kind: UnitKind,
  options: { subtype?: string; bits?: string; body?: string } = {},
): Api.IsccUnit {
  const bits = options.bits ?? seedBits(`fixture-${kind}`, 64);
  const subtype = options.subtype ?? (kind === "content" || kind === "semantic" ? "IMAGE" : "NONE");
  return {
    iscc_unit: `ISCC:${HEAD[kind]}${options.body ?? "WN77F73NA44D7"}`,
    readable: `${READABLE[kind]}-${subtype}-V0-${bits.length}-abcdef0123456789`,
    hash_hex: "abcdef0123456789",
    hash_uint: "12345678901234567890",
    hash_bits: bits,
  };
}

export function fourUnits(): Api.IsccUnit[] {
  return [makeUnit("meta"), makeUnit("content"), makeUnit("data"), makeUnit("instance")];
}

export function makeExplain(units: Api.IsccUnit[], iscc: string = SAMPLE_ISCC): Api.IsccDecomposition {
  return {
    iscc,
    readable: "ISCC-IMAGE-V0-MCDI-abcdef0123456789",
    multiformat: "uzAFTBsinBjnrEWezZ6nDeHxlweWC4uZi9yi0",
    decomposed: units.map((u) => u.iscc_unit.replace("ISCC:", "")).join("-"),
    units,
  };
}

export function makeMetadata(overrides: Partial<Api.IsccMetadata> = {}): Api.IsccMetadata {
  return {
    iscc: SAMPLE_ISCC,
    media_id: "061kcmrj55fi8",
    content: "/api/v1/media/061kcmrj55fi8",
    name: "test image",
    description: "",
    mode: "image",
    filename: "test-image.jpg",
    filesize: 53256,
    mediatype: "image/jpeg",
    width: 200,
    height: 133,
    units: fourUnits().map((u) => u.iscc_unit),
    ...overrides,
  };
}

export function makeSpecimen(overrides: Partial<IsccWeb.Specimen> = {}): IsccWeb.Specimen {
  return {
    id: "spec-1",
    kind: "file",
    label: "test-image.jpg",
    status: "done",
    progress: 100,
    bytesUploaded: 53256,
    bytesTotal: 53256,
    typeHint: "image/jpeg",
    startedAt: 0,
    elapsed: 1.8,
    error: null,
    semantic: false,
    granular: false,
    metadata: makeMetadata(),
    explain: makeExplain(fourUnits()),
    previewUrl: null,
    metadataChanged: false,
    embedBusy: false,
    embedError: null,
    compareWithId: null,
    compareSwapped: false,
    ...overrides,
  };
}
