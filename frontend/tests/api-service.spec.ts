/** Tests for the REST API wrapper in services/api.service.ts. */
import { afterEach, describe, expect, it, vi } from "vitest";
import { Base64 } from "js-base64";
import { apiService } from "../services/api.service";
import { makeMetadata } from "./fixtures";

const jsonResponse = (data: unknown, ok = true, status = 200) =>
  ({
    ok,
    status,
    json: async () => data,
    text: async () => (typeof data === "string" ? data : JSON.stringify(data)),
  }) as Response;

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("isccEndpoint", () => {
  it("always sends both generation options explicitly", () => {
    expect(apiService.isccEndpoint(true, false)).toBe("/api/v1/iscc?semantic=true&granular=false");
    expect(apiService.isccEndpoint(false, true)).toBe("/api/v1/iscc?semantic=false&granular=true");
  });
});

describe("createIsccFromText", () => {
  it("POSTs the raw text with a base64 filename header", async () => {
    const fetchMock = vi.fn(async () => jsonResponse(makeMetadata()));
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiService.createIsccFromText("hello world", true, false);

    expect(result.iscc).toBe(makeMetadata().iscc);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/v1/iscc?semantic=true&granular=false");
    expect(init.method).toBe("POST");
    expect(init.body).toBe("hello world");
    expect((init.headers as Record<string, string>)["X-Upload-Filename"]).toBe(Base64.encode("pasted-text.txt"));
  });

  it("throws with status and body on errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse("boom", false, 422)),
    );
    await expect(apiService.createIsccFromText("x", false, false)).rejects.toThrow("422: boom");
  });
});

describe("explainIscc", () => {
  it("GETs the explain endpoint for the code", async () => {
    const fetchMock = vi.fn(async () => jsonResponse({ iscc: "ISCC:KACYPXW445FTYNJ3", units: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await apiService.explainIscc("ISCC:KACYPXW445FTYNJ3");

    const [url] = fetchMock.mock.calls[0] as unknown as [string];
    expect(url).toBe("/api/v1/explain/ISCC:KACYPXW445FTYNJ3");
  });
});

describe("embedMetadata", () => {
  it("POSTs JSON to the metadata endpoint", async () => {
    const fetchMock = vi.fn(async () => jsonResponse(makeMetadata()));
    vi.stubGlobal("fetch", fetchMock);

    await apiService.embedMetadata("061kcmrj55fi8", { name: "A title", description: "A description" });

    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/v1/metadata/061kcmrj55fi8");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string)).toEqual({ name: "A title", description: "A description" });
  });
});

describe("deleteMedia / downloadUrl", () => {
  it("DELETEs the media package", async () => {
    const fetchMock = vi.fn(async () => jsonResponse(null, true, 204));
    vi.stubGlobal("fetch", fetchMock);

    await apiService.deleteMedia("061kcmrj55fi8");

    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/v1/media/061kcmrj55fi8");
    expect(init.method).toBe("DELETE");
  });

  it("builds the download link", () => {
    expect(apiService.downloadUrl("061kcmrj55fi8")).toBe("/api/v1/media/061kcmrj55fi8");
  });
});
