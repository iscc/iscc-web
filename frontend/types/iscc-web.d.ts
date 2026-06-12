type Nullable<T> = T | null;

declare namespace IsccWeb {
  type SpecimenKind = "file" | "text" | "code";
  type SpecimenStatus = "uploading" | "processing" | "done" | "error";

  /** One generated or decoded result in the feed, driving a single readout card. */
  export interface Specimen {
    id: string;
    kind: SpecimenKind;
    label: string;
    status: SpecimenStatus;
    /** Upload progress 0-100 (file kind only). */
    progress: number;
    bytesUploaded: number;
    bytesTotal: number;
    /** Client-side media type hint before the server response arrives. */
    typeHint: string;
    /** performance.now() when intake started; used for the elapsed display. */
    startedAt: number;
    /** Seconds from intake to readout, set when status becomes done. */
    elapsed: Nullable<number>;
    error: Nullable<string>;
    /** Generation options in effect when this specimen was created. */
    semantic: boolean;
    granular: boolean;
    metadata: Nullable<Api.IsccMetadata>;
    explain: Nullable<Api.IsccDecomposition>;
    /** Client-side object URL for instant image previews. */
    previewUrl: Nullable<string>;
    /** True once metadata was embedded — an updated file copy is downloadable. */
    metadataChanged: boolean;
    embedBusy: boolean;
    embedError: Nullable<string>;
    /** Id of the docked comparison specimen (B), if any. */
    compareWithId: Nullable<string>;
    /** Swap A/B display order inside the docked comparison. */
    compareSwapped: boolean;
  }

  export interface MetadataFormData {
    name: string;
    description: string;
  }
}
