class ApiService {
  public async embedMetadata(mediaId: string, formData: IsccWeb.MetadataFormData): Promise<Api.IsccMetadata> {
    const response = await fetch(`/api/v1/metadata/${mediaId}`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json;charset=UTF-8",
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error(`${response.status}: ${await response.text()}`);
    }

    return (await response.json()) as Api.IsccMetadata;
  }
}

export const apiService = new ApiService();
