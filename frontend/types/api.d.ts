declare namespace Api {
  export interface IsccMetadata {
    "@context": string;
    "@type": "CreativeWork" | "TextDigitalDocument" | "ImageObject" | "AudioObject" | "VideoObject";
    $schema: string;
    iscc: string;
    content: string;
    media_id: string;
    name: string;
    description: string;
    meta: string;
    creator: string;
    license: string;
    acquire: string;
    credit: string;
    rights: string;
    mode: "text" | "image" | "audio" | "video" | "mixed";
    filename: string;
    filesize: number;
    mediatype: string;
    duration: number;
    fps: number;
    width: number;
    height: number;
    characters: number;
    language: string;
    thumbnail: string;
    units?: Array<string>;
    features?: Array<Api.FeatureSet>;
  }

  export interface FeatureSet {
    maintype: string;
    subtype: string;
    version: number;
    byte_offsets: boolean;
    simprints: Array<string>;
    offsets?: Array<number>;
    sizes?: Array<number>;
  }

  export interface IsccUnit {
    iscc_unit: string;
    readable: string;
    hash_hex: string;
    hash_uint: string;
    hash_bits: string;
  }

  export interface IsccDecomposition {
    iscc: string;
    readable: string;
    multiformat: string;
    decomposed: string;
    units: Array<Api.IsccUnit>;
  }
}
