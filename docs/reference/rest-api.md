---
icon: lucide/braces
description: Complete REST API reference - endpoints, parameters, headers, response shapes, and curl examples.
---

# REST API

All endpoints live under the base path `/api/v1`. The OpenAPI 3.0 document at
`iscc_web/static/docs/openapi.yaml` is the source of truth for the API; every running instance
serves interactive API documentation (Stoplight Elements) at `/docs` and the raw spec at
`/docs/openapi.yaml`. Examples below target a local instance at `http://localhost:8000` — the
public demo instance is <https://web.iscc.io>.

## Conventions

| Topic          | Behavior                                                                                                                                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Uploads        | Raw request body (**not** multipart/form-data). The filename travels base64-encoded in the `X-Upload-Filename` header.                                                                                       |
| `Content-Type` | Send the file's media type if known. It is stored with the upload and echoed as the `Content-Type` of later downloads.                                                                                       |
| `media_id`     | Server-generated, 13 lowercase characters matching `[a-v0-9]{13}`. Other values do not match the route and yield `404`.                                                                                      |
| Storage expiry | Uploads are deleted automatically after `ISCC_WEB_STORAGE_EXPIRY` seconds (default `3600`); the cleanup task runs every `ISCC_WEB_CLEANUP_INTERVAL` seconds (default `600`). Expired resources return `404`. |
| Upload size    | Bodies larger than `ISCC_WEB_MAX_UPLOAD_SIZE` bytes (default `1073741824` = 1 GiB) and empty bodies are rejected with `400`.                                                                                 |
| Private files  | With `ISCC_WEB_PRIVATE_FILES=true` (the default), download, delete, and metadata embedding are restricted to the original uploader (identified by a hash of the client IP) and return `403` for anyone else. |
| Errors         | Error responses are plain-text status messages, not JSON.                                                                                                                                                    |

See [Configuration](../howto/configuration.md) for all `ISCC_WEB_*` and `ISCC_SDK_*` options.

### Endpoint overview

| Method   | Path                   | Purpose                                                     |
| -------- | ---------------------- | ----------------------------------------------------------- |
| `POST`   | `/iscc`                | Upload a file and create its ISCC                           |
| `GET`    | `/iscc/{media_id}`     | Retrieve a previously created ISCC result                   |
| `POST`   | `/media`               | Upload a file without ISCC processing                       |
| `GET`    | `/media/{media_id}`    | Download an uploaded file                                   |
| `DELETE` | `/media/{media_id}`    | Delete an uploaded file                                     |
| `GET`    | `/metadata/{media_id}` | Extract embedded metadata from a file                       |
| `POST`   | `/metadata/{media_id}` | Embed metadata into a copy of a file and re-create its ISCC |
| `GET`    | `/explain/{iscc}`      | Decompose an ISCC into its units and representations        |
| `POST`   | `/simprint`            | Create granular simprints from plain text                   |

## ISCC

### POST /iscc

Upload a media file and generate its ISCC. Returns ISCC metadata including the composite
ISCC-CODE, individual ISCC-UNITs, technical metadata, and a thumbnail where applicable.

| Parameter           | In     | Type    | Required | Description                                                                                                                                                                                     |
| ------------------- | ------ | ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `X-Upload-Filename` | header | string  | yes      | Base64-encoded filename of the upload.                                                                                                                                                          |
| `semantic`          | query  | boolean | no       | Add an experimental Semantic-Code ISCC-UNIT (text and image content) to the composite ISCC-CODE — 5 units instead of 4. Default: service setting `ISCC_WEB_SEMANTIC_DEFAULT` (ships `false`).   |
| `granular`          | query  | boolean | no       | Include granular simprint features in the `features` field (text content only; with `semantic=true` also semantic text simprints). Default: service setting `ISCC_SDK_GRANULAR` (ships `true`). |

Request body: the raw file bytes (`application/octet-stream` or the file's actual media type).

!!! warning "Experimental 5-unit codes"

    With `semantic=true` the resulting ISCC-CODE contains five units (Meta, Semantic, Content,
    Data, Instance) and is **not** a standard ISO 24138 identifier. Semantic-Code and simprint
    algorithms may change before their v1.0 release.

| Status | Meaning                                                                                            |
| ------ | -------------------------------------------------------------------------------------------------- |
| `201`  | Created. `Location` header holds the root-relative media URL (e.g. `/api/v1/media/061kcmrj55fi8`). |
| `400`  | Missing/invalid `X-Upload-Filename`, body size out of range, or invalid query parameter value.     |
| `422`  | ISCC processing error.                                                                             |

Unsupported media types do not fail by default: with `ISCC_SDK_FALLBACK=true` (the default) they
produce a wide 2-unit ISCC-SUM (Data + Instance) instead of `422`.

=== "bash"

    ```shell
    curl -X POST "http://localhost:8000/api/v1/iscc?semantic=false&granular=true" \
      -H "X-Upload-Filename: $(printf 'test-image.jpg' | base64)" \
      -H "Content-Type: image/jpeg" \
      --data-binary @test-image.jpg
    ```

=== "PowerShell"

    ```powershell
    $filename = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("test-image.jpg"))
    curl.exe -X POST "http://localhost:8000/api/v1/iscc?semantic=false&granular=true" `
      -H "X-Upload-Filename: $filename" `
      -H "Content-Type: image/jpeg" `
      --data-binary "@test-image.jpg"
    ```

Response (`201`, thumbnail truncated):

```json
{
  "@context": "http://purl.org/iscc/context/0.8.0.jsonld",
  "@type": "ImageObject",
  "$schema": "http://purl.org/iscc/schema/0.8.0.json",
  "iscc": "ISCC:KECXNDSZVTTX2LDQYNBTBHR4T2HGOYBAGBNWZ767PKO3JQGZ42GFEAY",
  "media_id": "061kcmrj55fi8",
  "content": "http://localhost:8000/api/v1/media/061kcmrj55fi8",
  "name": "test image",
  "mode": "image",
  "filename": "test-image.jpg",
  "filesize": 53256,
  "mediatype": "image/jpeg",
  "width": 200,
  "height": 133,
  "thumbnail": "data:image/webp;base64,UklGRtIFAABXRUJQVlA4IMYFAADwIQCdASqAAFUAPxF0...",
  "generator": "iscc-sdk - v0.9.3",
  "metahash": "1e20304ab0c98a760be580dfa20716f2912d7ae30ec82b5f48b01dcf8f008d42568d",
  "datahash": "1e209db4c0d9e68c5203dc8c2fefe52fa5d54671be3a3253e06888cace7c60e5a743",
  "units": [
    "ISCC:AADXNDSZVTTX2LDQWWLJUWUK3DGIQV27EFWEUI2AEXNONCRDWUSE2OY",
    "ISCC:EED4GQZQTY6J5DTHQ2DWCPDZHQOM6QZQTY6J5DTFZ2DWCPDZHQOMXDI",
    "ISCC:GADWAIBQLNWP7X32J3INMAMDUJ4QMN67BBQKVTVZIWHXQ7QJIKHYTBY",
    "ISCC:IADZ3NGA3HTIYUQD3SGC737FF6S5KRTRXY5DEU7ANCEMVTT4MDS2OQY"
  ]
}
```

For text uploads with granular features enabled, the response additionally carries a `features`
array of feature sets:

| Field                  | Type              | Description                                                                               |
| ---------------------- | ----------------- | ----------------------------------------------------------------------------------------- |
| `maintype` / `subtype` | string            | Simprint algorithm type, e.g. `content`/`text` or `semantic`/`text`.                      |
| `version`              | integer           | Algorithm version (currently `0`).                                                        |
| `byte_offsets`         | boolean           | Whether offsets are UTF-8 byte positions instead of character positions (default `true`). |
| `simprints`            | array of strings  | Base64-encoded 256-bit similarity-preserving fingerprints.                                |
| `offsets` / `sizes`    | array of integers | Position and size of each fingerprinted segment.                                          |

### GET /iscc/{media_id}

Return the stored ISCC result for a previous `POST /iscc` upload. The stored result omits the
volatile `media_id` and `content` fields.

| Status | Meaning                                                  |
| ------ | -------------------------------------------------------- |
| `200`  | ISCC metadata as `application/json`.                     |
| `404`  | No ISCC result for this `media_id` (unknown or expired). |

```shell
curl http://localhost:8000/api/v1/iscc/061knt35ejv6o
```

## Media

### POST /media

Upload a file without ISCC processing (e.g. as preparation for metadata extraction).

| Parameter           | In     | Type   | Required | Description                            |
| ------------------- | ------ | ------ | -------- | -------------------------------------- |
| `X-Upload-Filename` | header | string | yes      | Base64-encoded filename of the upload. |

Request body: the raw file bytes.

| Status | Meaning                                                        |
| ------ | -------------------------------------------------------------- |
| `201`  | Created. `Location` header holds the root-relative media URL.  |
| `400`  | Missing/invalid `X-Upload-Filename` or body size out of range. |

```shell
curl -X POST http://localhost:8000/api/v1/media \
  -H "X-Upload-Filename: $(printf 'test-image.jpg' | base64)" \
  -H "Content-Type: image/jpeg" \
  --data-binary @test-image.jpg
```

Response (`201`):

```json
{
  "content": "http://localhost:8000/api/v1/media/061knt35ejv6o",
  "media_id": "061knt35ejv6o"
}
```

### GET /media/{media_id}

Download an uploaded file. The response streams the original bytes with the `Content-Type`
recorded at upload time and a `Content-Disposition` attachment filename.

| Status | Meaning                                                                                 |
| ------ | --------------------------------------------------------------------------------------- |
| `200`  | File content.                                                                           |
| `403`  | `ISCC_WEB_PRIVATE_FILES=true` and the request does not come from the original uploader. |
| `404`  | Unknown or expired `media_id`.                                                          |

```shell
curl -OJ http://localhost:8000/api/v1/media/061knt35ejv6o
```

### DELETE /media/{media_id}

Delete an uploaded file and all stored results for it.

| Status | Meaning                                                                                 |
| ------ | --------------------------------------------------------------------------------------- |
| `204`  | Deleted.                                                                                |
| `403`  | `ISCC_WEB_PRIVATE_FILES=true` and the request does not come from the original uploader. |
| `404`  | Unknown or expired `media_id`.                                                          |

```shell
curl -X DELETE http://localhost:8000/api/v1/media/061knt35ejv6o
```

## Metadata

### GET /metadata/{media_id}

Extract metadata embedded in an uploaded media file. Returns only fields that are present:
`name`, `description`, `meta`, `identifier`, `creator`, `license`, `acquire`, `credit`,
`rights`.

| Status | Meaning                        |
| ------ | ------------------------------ |
| `200`  | Extracted metadata as JSON.    |
| `404`  | Unknown or expired `media_id`. |

```shell
curl http://localhost:8000/api/v1/metadata/061knt35ejv6o
```

Response (`200`):

```json
{
  "name": "Concentrated Cat PNG",
  "creator": "Another Cat Lover"
}
```

### POST /metadata/{media_id}

Embed metadata into a media file and reprocess its ISCC. The original file is not modified —
a copy is created under a new `media_id`; the response `content` field links to the new file,
which clients should offer for download.

Request body (`application/json`) — all fields optional:

| Field         | Type                       | Description                                                      |
| ------------- | -------------------------- | ---------------------------------------------------------------- |
| `name`        | string (≤ 128)             | Title of the work. Input for ISCC Meta-Code generation.          |
| `description` | string (≤ 4096)            | Description of the content. Input for ISCC Meta-Code generation. |
| `meta`        | string (≤ 16384)           | Industry- or use-case-specific metadata as a Data-URL.           |
| `identifier`  | string                     | Other identifier(s) referencing the work.                        |
| `creator`     | string                     | Entity primarily responsible for the resource.                   |
| `license`     | string                     | URI of the license for the content.                              |
| `acquire`     | string (URI)               | URL of a page where a license can be acquired.                   |
| `credit`      | string                     | Credit line to display alongside the content.                    |
| `rights`      | string                     | Copyright notice.                                                |
| `keywords`    | string or array of strings | Keywords or tags describing the content.                         |

| Status | Meaning                                                                                 |
| ------ | --------------------------------------------------------------------------------------- |
| `201`  | Created. ISCC metadata for the new file; `Location` header points to it.                |
| `400`  | Invalid request body.                                                                   |
| `403`  | `ISCC_WEB_PRIVATE_FILES=true` and the request does not come from the original uploader. |
| `404`  | Unknown or expired `media_id`.                                                          |
| `422`  | Embedding or ISCC processing failed (e.g. media type without embedding support).        |

!!! note

    This endpoint has no `semantic`/`granular` parameters — reprocessing always uses the
    service defaults. Embedding into a file whose original ISCC was created with
    `semantic=true` therefore returns a standard 4-unit code unless the service enables
    `ISCC_SDK_EXPERIMENTAL` globally.

```shell
curl -X POST http://localhost:8000/api/v1/metadata/061knt35ejv6o \
  -H "Content-Type: application/json" \
  -d '{"name": "The Never Ending Story", "creator": "Joanne K. Rowling"}'
```

The `201` response has the same shape as `POST /iscc`, with the new `media_id`/`content` and the
submitted metadata merged in (e.g. `"iscc": "ISCC:KECTN76LTY522ZPCYNBTBHR4T2HGO6RDNMJX4P6UMT5X2NVXB7F2FGA"`,
`"name": "The Never Ending Story"`, `"creator": "Another Cat Lover, Joanne K. Rowling"`).

## Explain

### GET /explain/{iscc}

Decompose an ISCC and return alternative representations of the code and each of its units.
Accepts canonical codes with or without the `ISCC:` prefix. This endpoint requires no upload
and works on any valid ISCC.

| Status | Meaning                |
| ------ | ---------------------- |
| `200`  | Decomposition as JSON. |
| `400`  | Invalid ISCC.          |

```shell
curl http://localhost:8000/api/v1/explain/ISCC:KMDMRJYGHHVRCZ5TM6U4G6D4MXA6LAXC4ZRPOKFU7JBEQXR2BJOS6NA
```

Response (`200`, units abbreviated):

```json
{
  "iscc": "ISCC:KMDMRJYGHHVRCZ5TM6U4G6D4MXA6LAXC4ZRPOKFU7JBEQXR2BJOS6NA",
  "readable": "ISCC-VIDEO-V0-MSDI-c8a70639eb1167b367a9c3787c65c1e582e2e662f728b4fa42485e3a0a5d2f34",
  "multiformat": "uzAFTBsinBjnrEWezZ6nDeHxlweWC4uZi9yi0-kJIXjoKXS80",
  "decomposed": "AAA4RJYGHHVRCZ5T-CMAWPKODPB6GLQPF-GAAYFYXGML3SRNH2-IAAUESC6HIFF2LZU",
  "units": [
    {
      "iscc_unit": "ISCC:AAA4RJYGHHVRCZ5T",
      "readable": "META-NONE-V0-64-c8a70639eb1167b3",
      "hash_hex": "c8a70639eb1167b3",
      "hash_uint": "14458531974522955699",
      "hash_bits": "1100100010100111000001100011100111101011000100010110011110110011"
    }
  ]
}
```

## Simprint

### POST /simprint

Generate granular simprints from plain text for similarity search. The output format is
compatible with [iscc-search](https://github.com/iscc/iscc-search) and the granular `features`
of `POST /iscc`. Simprint algorithms are experimental and may change before their v1.0 release.

Request body (`application/json`):

| Field  | Type   | Required | Description                                                                  |
| ------ | ------ | -------- | ---------------------------------------------------------------------------- |
| `text` | string | yes      | Plain text input, non-empty, at most `ISCC_WEB_MAX_UPLOAD_SIZE` UTF-8 bytes. |

| Status | Meaning                                                                                                                                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `200`  | Simprints keyed by simprint type: `CONTENT_TEXT_V0` (256-bit minhash simprints, one per content-defined text chunk) and `SEMANTIC_TEXT_V0` (256-bit semantic simprints via [iscc-sct](https://github.com/iscc/iscc-sct)). |
| `400`  | Missing, empty, oversized, or non-JSON input.                                                                                                                                                                             |
| `422`  | Simprint processing error.                                                                                                                                                                                                |

```shell
curl -X POST http://localhost:8000/api/v1/simprint \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World! This is a short text for simprint generation."}'
```

Response (`200`):

```json
{
  "CONTENT_TEXT_V0": [
    "SCXX_obwF2sK-xsnk9p1hhsH1fvrzwyZZBhhsVxMLTM"
  ],
  "SEMANTIC_TEXT_V0": [
    "emhK25dQAqnkcdcMuworif5t5GzDy8A3zmlDCEdAyWk"
  ]
}
```
