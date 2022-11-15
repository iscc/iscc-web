declare namespace IsccWeb {
  export interface FileUpload {
    id: string;
    name: string;
    progress: number;
    status: "UPLOADING" | "PROCESSING" | "PROCESSED" | "UPDATING_METADATA" | "ERROR";
    isccMetadata: Nullable<Api.IsccMetadata>;
    metadataChanged: boolean;
    error: Nullable<Error>;
    hashBits: Nullable<string>;
  }

  export interface MetadataFormData {
    name: string;
    description: string;
  }
}
