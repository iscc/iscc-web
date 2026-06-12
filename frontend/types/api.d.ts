declare namespace Api {
  /** ISCC Metadata returned by POST /iscc, GET /iscc/{media_id} and POST /metadata/{media_id}. */
  export interface IsccMetadata {
    "@context"?: string;
    "@type"?: "CreativeWork" | "TextDigitalDocument" | "ImageObject" | "AudioObject" | "VideoObject";
    $schema?: string;
    iscc: string;
    content?: string;
    media_id?: string;
    name?: string;
    description?: string;
    meta?: string;
    creator?: string;
    license?: string;
    acquire?: string;
    credit?: string;
    rights?: string;
    keywords?: string | Array<string>;
    mode?: "text" | "image" | "audio" | "video" | "mixed";
    filename?: string;
    filesize?: number;
    mediatype?: string;
    duration?: number;
    fps?: number;
    width?: number;
    height?: number;
    characters?: number;
    language?: string;
    thumbnail?: string;
    generator?: string;
    metahash?: string;
    datahash?: string;
    units?: Array<string>;
    features?: Array<Api.FeatureSet>;
  }

  /** Granular simprint features paired with their algorithm metadata. */
  export interface FeatureSet {
    maintype: string;
    subtype: string;
    version: number;
    byte_offsets: boolean;
    simprints: Array<string>;
    offsets?: Array<number>;
    sizes?: Array<number>;
  }

  /** One ISCC-UNIT in the representations returned by GET /explain/{iscc}. */
  export interface IsccUnit {
    iscc_unit: string;
    readable: string;
    hash_hex: string;
    hash_uint: string;
    hash_bits: string;
  }

  /** Decomposition of an ISCC returned by GET /explain/{iscc}. */
  export interface IsccDecomposition {
    iscc: string;
    readable: string;
    multiformat: string;
    decomposed: string;
    units: Array<Api.IsccUnit>;
  }
}
