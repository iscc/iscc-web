declare namespace IsccWeb {
  export interface FileUpload {
    id: string;
    name: string;
    progress: number;
    status: "UPLOADING" | "PROCESSING" | "PROCESSED" | "UPDATING_METADATA" | "ERROR";
    isccMetadata: Nullable<Api.IsccMetadata>;
    error: Nullable<Error>;
  }

  export interface MetadataFormData {
    name: string;
    description: string;
  }
}
