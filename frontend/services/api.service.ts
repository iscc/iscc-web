/** Thin typed wrapper around the iscc-web REST API. */
import { Base64 } from "js-base64";

async function expectJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`${response.status}: ${await response.text()}`);
  }
  return (await response.json()) as T;
}

class ApiService {
  /** Upload endpoint with explicit generation options (also used by the Uppy uploader). */
  public isccEndpoint(semantic: boolean, granular: boolean): string {
    const params = new URLSearchParams({ semantic: String(semantic), granular: String(granular) });
    return `/api/v1/iscc?${params.toString()}`;
  }

  /** Generate an ISCC for pasted plain text (uploaded as pasted-text.txt). */
  public async createIsccFromText(text: string, semantic: boolean, granular: boolean): Promise<Api.IsccMetadata> {
    const response = await fetch(this.isccEndpoint(semantic, granular), {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "text/plain;charset=UTF-8",
        "X-Upload-Filename": Base64.encode("pasted-text.txt"),
      },
      body: text,
    });
    return expectJson<Api.IsccMetadata>(response);
  }

  /** Decompose an ISCC into its units with bit-level representations. */
  public async explainIscc(iscc: string): Promise<Api.IsccDecomposition> {
    const response = await fetch(`/api/v1/explain/${iscc}`, {
      headers: { Accept: "application/json" },
    });
    return expectJson<Api.IsccDecomposition>(response);
  }

  /** Embed metadata into a copy of the media file and reprocess its ISCC. */
  public async embedMetadata(mediaId: string, formData: IsccWeb.MetadataFormData): Promise<Api.IsccMetadata> {
    const response = await fetch(`/api/v1/metadata/${mediaId}`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json;charset=UTF-8",
      },
      body: JSON.stringify(formData),
    });
    return expectJson<Api.IsccMetadata>(response);
  }

  /** Delete an uploaded media package (best effort; 404s are fine). */
  public async deleteMedia(mediaId: string): Promise<void> {
    await fetch(`/api/v1/media/${mediaId}`, { method: "DELETE" });
  }

  /** Download link for an uploaded media file. */
  public downloadUrl(mediaId: string): string {
    return `/api/v1/media/${mediaId}`;
  }
}

export const apiService = new ApiService();
