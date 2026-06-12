---
icon: lucide/house
description: A microservice for generating International Standard Content Codes (ISCC, ISO 24138) for media files - REST API, metadata embedding, ISCC decoding, and a Vue.js demo frontend.
---

# iscc-web

[![CI](https://github.com/iscc/iscc-web/actions/workflows/ci.yml/badge.svg)](https://github.com/iscc/iscc-web/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/iscc/iscc-web/blob/main/LICENSE)

**A microservice for generating International Standard Content Codes
([ISCC](https://iscc.codes), ISO 24138) for media files.**

!!! tip "Try it without installing anything"

    A public instance runs at [iscc.io](https://iscc.io) - upload a file in the demo frontend or
    explore the interactive API documentation at [iscc.io/docs](https://iscc.io/docs).

## Introduction

`iscc-web` is a Python ASGI application built on
[BlackSheep](https://github.com/Neoteroi/BlackSheep) that wraps the
[iscc-sdk](https://github.com/iscc/iscc-sdk) behind a REST API. Upload a media file and get back
its ISCC with rich metadata; the same service extracts and embeds metadata, decodes existing
ISCCs, and generates granular text fingerprints for similarity search.

**Key features:**

- **ISCC generation** - upload any media file, receive its composite ISCC-CODE with ISCC-UNITs
    and technical metadata
- **Metadata extraction & embedding** - read embedded metadata, or embed ISCC metadata into a
    copy of the file and reprocess its ISCC
- **ISCC decoding** - decompose any ISCC into human-readable units via the explain endpoint
- **Plain-text simprints** - granular similarity fingerprints compatible with
    [iscc-search](https://github.com/iscc/iscc-search)
- **Automatic expiry** - uploaded files are deleted after a configurable timeout (default 1 hour)
- **Private by default** - file downloads and deletes are restricted to the original uploader
- **Interactive API docs** - OpenAPI 3 spec with a Stoplight Elements UI served at `/docs`
- **Demo frontend** - Vue 3 single-page app for uploading files, decoding ISCCs, embedding
    metadata, and comparing codes

All endpoints live under the `/api/v1` base path:

| Endpoint                       | Purpose                                     |
| ------------------------------ | ------------------------------------------- |
| `POST /iscc`                   | Upload a file and generate its ISCC         |
| `GET /iscc/{media_id}`         | Retrieve a previously generated ISCC        |
| `POST /media`                  | Upload a file without ISCC processing       |
| `GET/DELETE /media/{media_id}` | Download or delete an uploaded file         |
| `GET /metadata/{media_id}`     | Extract embedded metadata                   |
| `POST /metadata/{media_id}`    | Embed metadata and reprocess the ISCC       |
| `GET /explain/{iscc}`          | Decompose an ISCC into its units            |
| `POST /simprint`               | Generate granular simprints from plain text |

See the [REST API reference](reference/rest-api.md) for request and response details.

## Experimental features

The following features are not part of ISO 24138, and their algorithms may change before their
v1.0 release:

- `POST /api/v1/iscc?semantic=true` generates a Semantic-Code ISCC-UNIT for text
    ([iscc-sct](https://github.com/iscc/iscc-sct)) and image
    ([iscc-sci](https://github.com/iscc/iscc-sci)) content that becomes part of the composite
    ISCC-CODE - 5 units (Meta, Semantic, Content, Data, Instance) instead of 4. The resulting
    ISCC-CODE is **not** a standard ISO 24138 identifier. Off by default.
- `POST /api/v1/iscc` includes granular simprint features in the `features` field by default
    (text content; with `semantic=true` also semantic simprints). Simprints are 256-bit
    fingerprints with UTF-8 byte based offsets and sizes. Opt out per request with
    `?granular=false`.
- `POST /api/v1/simprint` generates granular simprints from plain text - byte-identical to
    [iscc-search](https://github.com/iscc/iscc-search)'s local simprint generation, so search
    services can delegate text processing to this service.

## Quick start

=== "Docker"

    ```bash
    docker run -p 8000:8000 ghcr.io/iscc/iscc-web:main
    ```

    The `:main` tag tracks the main branch; immutable semver tags are published on releases.
    The image ships with all content processing tools and semantic-code models pre-installed.

=== "From source"

    Requires [uv](https://docs.astral.sh/uv/), which provisions the required Python version
    automatically:

    ```bash
    git clone https://github.com/iscc/iscc-web.git
    cd iscc-web
    uv sync
    uv run iscc-web
    ```

The service is now available at <http://localhost:8000>. Generate your first ISCC by sending the
raw file bytes (not multipart form data) with the base64-encoded filename in the
`X-Upload-Filename` header:

```bash
curl -X POST http://localhost:8000/api/v1/iscc \
    -H "X-Upload-Filename: $(printf 'image.jpg' | base64)" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @image.jpg
```

The response is an [ISCC metadata](https://schema.iscc.codes) JSON object with the `iscc` code,
its `units`, and technical metadata. Continue with the
[getting started tutorial](tutorials/getting-started.md) for a full walk-through.

## Documentation

<div class="grid cards" markdown>

- **[Tutorials](tutorials/getting-started.md)** - Learn the basics

    Hands-on guide from installation to your first generated ISCC.

- **[How-to guides](howto/deployment.md)** - Solve specific problems

    Recipes for [deployment](howto/deployment.md) and [configuration](howto/configuration.md).

- **[Explanation](explanation/architecture.md)** - Understand the design

    Architecture of the API layer, worker pool, storage model, and frontend integration.

- **[Reference](reference/rest-api.md)** - API details

    [REST API reference](reference/rest-api.md) and a
    [guide for coding agents](reference/for-coding-agents.md).

</div>

[Development & Contributing](development/contributing.md) -
Dev setup, testing, and contribution guidelines.

[Source code on GitHub :lucide-external-link:](https://github.com/iscc/iscc-web){ .md-button }
