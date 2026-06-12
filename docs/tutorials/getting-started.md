---
icon: lucide/rocket
description: Run iscc-web with Docker or from source, generate your first ISCC by uploading a file with curl, try the experimental toggles, and decode the result.
---

# Getting started

Run the `iscc-web` service locally, generate your first ISCC by uploading a media file with
`curl`, and decode the result.

## Prerequisites

- [Docker](https://docs.docker.com/get-started/get-docker/), or
    [`uv`](https://docs.astral.sh/uv/) and `git` to run from source
- `curl` and a media file to fingerprint — any JPEG image works well for a first try

!!! tip

    No local setup at all? The public instance at [iscc.io](https://iscc.io) serves the same
    API — replace `http://localhost:8000` with `https://iscc.io` in the examples below.

## Start the service

=== "Docker"

    ```shell
    docker run --rm -p 8000:8000 ghcr.io/iscc/iscc-web:main
    ```

    The image ships with everything preinstalled: the content-processing binaries (ffmpeg,
    ffprobe, fpcalc), the ONNX models for the experimental semantic codes, and the prebuilt demo
    frontend. See [Deployment](../howto/deployment.md) for available tags and production setup.

=== "From source"

    ```shell
    git clone https://github.com/iscc/iscc-web.git
    cd iscc-web
    uv sync
    uv run iscc-web
    ```

    This starts a development server with auto-reload. For audio and video processing, fetch the
    content-processing binaries once with `uv run iscc-sdk install`. The demo frontend requires a
    separate build (see [Contributing](../development/contributing.md)); the REST API works
    without it.

The service listens at `http://localhost:8000` — configurable via `ISCC_WEB_SITE_ADDRESS`, or the
`PORT` environment variable in the Docker image.

## Generate your first ISCC

`POST /api/v1/iscc` takes the file as the **raw request body** — not a multipart form — with the
filename passed base64-encoded in the `X-Upload-Filename` header:

=== "bash"

    ```bash
    curl -X POST "http://localhost:8000/api/v1/iscc" \
        -H "X-Upload-Filename: $(printf '%s' 'test-image.jpg' | base64)" \
        --data-binary @test-image.jpg
    ```

=== "PowerShell"

    ```powershell
    $filename = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("test-image.jpg"))
    curl.exe -X POST "http://localhost:8000/api/v1/iscc" `
      -H "X-Upload-Filename: $filename" `
      --data-binary "@test-image.jpg"
    ```

!!! warning

    Do not upload with `curl -F` — that sends `multipart/form-data`, but the endpoint reads the
    raw request body. Use `--data-binary @<file>` as shown above.

The service answers `201 Created` with a `Location` header pointing to the uploaded media
resource and an [ISCC metadata](https://schema.iscc.codes) object as the body (thumbnail
truncated, your values will differ):

```json
{
  "@context": "http://purl.org/iscc/context/0.8.0.jsonld",
  "@type": "ImageObject",
  "$schema": "http://purl.org/iscc/schema/0.8.0.json",
  "iscc": "ISCC:KECXNDSZVTTX2LDQYNBTBHR4T2HGOYBAGBNWZ767PKO3JQGZ42GFEAY",
  "name": "test image",
  "media_id": "061kcmrj55fi8",
  "content": "http://localhost:8000/api/v1/media/061kcmrj55fi8",
  "mode": "image",
  "filename": "test-image.jpg",
  "filesize": 53256,
  "mediatype": "image/jpeg",
  "width": 200,
  "height": 133,
  "units": [
    "ISCC:AADXNDSZVTTX2LDQWWLJUWUK3DGIQV27EFWEUI2AEXNONCRDWUSE2OY",
    "ISCC:EED4GQZQTY6J5DTHQ2DWCPDZHQOM6QZQTY6J5DTFZ2DWCPDZHQOMXDI",
    "ISCC:GADWAIBQLNWP7X32J3INMAMDUJ4QMN67BBQKVTVZIWHXQ7QJIKHYTBY",
    "ISCC:IADZ3NGA3HTIYUQD3SGC737FF6S5KRTRXY5DEU7ANCEMVTT4MDS2OQY"
  ],
  "generator": "iscc-sdk - v0.9.3",
  "thumbnail": "data:image/webp;base64,UklGRtIFAABXRUJQVlA4IMYFAADwIQCdASqAAFUAPx...",
  "metahash": "1e20304ab0c98a760be580dfa20716f2912d7ae30ec82b5f48b01dcf8f008d42568d",
  "datahash": "1e209db4c0d9e68c5203dc8c2fefe52fa5d54671be3a3253e06888cace7c60e5a743"
}
```

The key fields:

| Field      | Meaning                                                                                                                          |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `iscc`     | The composite ISCC-CODE for the file.                                                                                            |
| `units`    | The ISCC-UNITs (Meta, Content, Data, Instance) at full 256-bit resolution; the composite `iscc` encodes a 64-bit digest of each. |
| `metahash` | Multihash (blake3) of the metadata used as Meta-Code input.                                                                      |
| `datahash` | Multihash (blake3) of the raw file bytes.                                                                                        |
| `name`     | Title used as Meta-Code input, extracted from embedded metadata when present.                                                    |
| `mode`     | Perceptual mode: `text`, `image`, `audio`, `video`, or `mixed`.                                                                  |
| `media_id` | Server-assigned upload ID, used by the other endpoints.                                                                          |
| `content`  | Download URL for the uploaded file.                                                                                              |

`filename`, `filesize`, `mediatype`, `width`, and `height` are technical metadata inferred from
the upload. The result stays retrievable at `GET /api/v1/iscc/{media_id}` until the upload
expires — after one hour by default (`ISCC_WEB_STORAGE_EXPIRY`).

!!! note

    Unsupported media types do not fail: the service falls back to a 2-unit ISCC-SUM (wide
    128-bit Data and Instance units) computed from the raw bytes.

## Try the experimental toggles

`POST /api/v1/iscc` accepts two optional boolean query parameters. Omitted parameters defer to
the service defaults; explicit values override per request:

| Parameter  | Default | Effect                                                                                                                                                                                                                                                                    |
| ---------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `semantic` | `false` | Folds an experimental Semantic-Code ISCC-UNIT (text via [iscc-sct](https://github.com/iscc/iscc-sct), image via [iscc-sci](https://github.com/iscc/iscc-sci)) into the composite ISCC-CODE — 5 units instead of 4. The result is **not** a standard ISO 24138 identifier. |
| `granular` | `true`  | Includes granular simprint features in the `features` field — 256-bit fingerprints with UTF-8 byte-based offsets and sizes, currently produced for text content (with `semantic=true` also semantic text simprints).                                                      |

```bash
curl -X POST "http://localhost:8000/api/v1/iscc?semantic=true&granular=true" \
    -H "X-Upload-Filename: $(printf '%s' 'article.txt' | base64)" \
    --data-binary @article.txt
```

With `semantic=true` the `units` array gains a fifth entry — the Semantic-Code unit, listed
between the Meta and Content units. For text content, granular output adds one `features` entry
per simprint type:

```json
"features": [
  {
    "maintype": "content",
    "subtype": "text",
    "version": 0,
    "byte_offsets": true,
    "simprints": ["k5TpwXVE3j9N5IBxm36c4hkXP6fHOv8bkY2f68_8XSg", "..."],
    "offsets": [0, 996],
    "sizes": [996, 457]
  }
]
```

Each simprint fingerprints one chunk of the extracted text; `offsets` and `sizes` locate the
chunks as UTF-8 byte positions. Both features are experimental — algorithms may change before
their v1.0 release. The service defaults are configurable; see
[Configuration](../howto/configuration.md).

## Decode any ISCC

`GET /api/v1/explain/{iscc}` decomposes an ISCC into its units and representations — it works for
any valid ISCC, not just codes generated by this service:

```bash
curl "http://localhost:8000/api/v1/explain/ISCC:KECXNDSZVTTX2LDQYNBTBHR4T2HGOYBAGBNWZ767PKO3JQGZ42GFEAY"
```

```json
{
  "iscc": "ISCC:KECXNDSZVTTX2LDQYNBTBHR4T2HGOYBAGBNWZ767PKO3JQGZ42GFEAY",
  "readable": "ISCC-IMAGE-V0-MCDI-768e59ace77d2c70c343309e3c9e8e676020305b6cffdf7a9db4c0d9e68c5203",
  "multiformat": "uzAFRBXaOWaznfSxww0MwnjyejmdgIDBbbP_fep20wNnmjFID",
  "decomposed": "AAAXNDSZVTTX2LDQ-EEA4GQZQTY6J5DTH-GAAWAIBQLNWP7X32-IAAZ3NGA3HTIYUQD",
  "units": [
    {
      "iscc_unit": "ISCC:AAAXNDSZVTTX2LDQ",
      "readable": "META-NONE-V0-64-768e59ace77d2c70",
      "hash_hex": "768e59ace77d2c70",
      "hash_uint": "8542864142321396848",
      "hash_bits": "0111011010001110010110011010110011100111011111010010110001110000"
    },
    ...
    {
      "iscc_unit": "ISCC:IAAZ3NGA3HTIYUQD",
      "readable": "INSTANCE-NONE-V0-64-9db4c0d9e68c5203",
      "hash_hex": "9db4c0d9e68c5203",
      "hash_uint": "11363919801870995971",
      "hash_bits": "1001110110110100110000001101100111100110100011000101001000000011"
    }
  ]
}
```

The `MCDI` subtype in `readable` names the units in the composite (Meta, Content, Data,
Instance), and each unit's body is shown as hex, unsigned integer, and bit pattern. Note how the
Instance-Code body `9db4c0d9e68c5203` is the leading 64 bits of the `datahash` from the upload
response. The endpoint also accepts the code without its `ISCC:` prefix.

## Explore the demo frontend and API docs

- **Demo frontend** at [http://localhost:8000/](http://localhost:8000/) — upload media files via
    drag and drop, paste plain text, generate and compare ISCCs, embed metadata, and inspect
    decoded units interactively.
- **Interactive API docs** at [http://localhost:8000/docs](http://localhost:8000/docs) — explore
    and try all endpoints, backed by the OpenAPI spec served at `/docs/openapi.yaml`.

## Next steps

- **[Deployment](../howto/deployment.md)** -- Run iscc-web in production with Docker Compose and
    Caddy.
- **[Configuration](../howto/configuration.md)** -- All `ISCC_WEB_*` options and the ISCC
    processing defaults.
- **[REST API reference](../reference/rest-api.md)** -- Every endpoint, parameter, and response
    schema.
- **[Architecture](../explanation/architecture.md)** -- How the service works under the hood.
