declare namespace IsccWeb {
  export interface FileUpload {
    id: string;
    name: string;
    progress: number;
    status: "UPLOADING" | "PROCESSING" | "PROCESSED" | "ERROR";
    isccMetadata: Nullable<Api.IsccMetadata>;
    error: Nullable<Error>;
  }
}
