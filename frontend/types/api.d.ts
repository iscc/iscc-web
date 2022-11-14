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
