# ISCC - Generator Microservice

[![CI](https://github.com/iscc/iscc-web/actions/workflows/ci.yml/badge.svg)](https://github.com/iscc/iscc-web/actions/workflows/ci.yml)

## About `iscc-web`

`iscc-web` is a microservice for generating **International Standard Content Codes**
([ISCC](https://iscc.codes)) for media files. A public instance of this service is available at
https://web.iscc.io

Full documentation is published at https://web.iscc.codes and release history is tracked in the
[changelog](https://web.iscc.codes/development/changelog/).

## Quickstart

Run the service with Docker (images are published to [ghcr.io](https://github.com/iscc/iscc-web/pkgs/container/iscc-web)
with `main` and semver tags):

```shell
docker run -p 8000:8000 ghcr.io/iscc/iscc-web:main
```

## Overview

<img align="left" width="200" src="docs/assets/iscc-web-rest-api.jpg?raw=true">

**REST API**

The microservice provides a REST API for generating ISCCs. The endpoints support file
upload/download, metadata extraction/embedding and ISCC processing.<br>

Files uploaded for processing are automatically deleted after a configurable timeout.
An interactive API documentation is available at [/docs](https://web.iscc.io/docs)<br><br>

**Experimental features** (not part of ISO 24138, algorithms may change before their v1.0
release):

- `POST /api/v1/iscc?semantic=true` generates an experimental Semantic-Code ISCC-UNIT for text
    ([iscc-sct](https://github.com/iscc/iscc-sct)) and image
    ([iscc-sci](https://github.com/iscc/iscc-sci)) content that becomes part of the composite
    ISCC-CODE - 5 units (Meta, Semantic, Content, Data, Instance) instead of 4. The resulting
    ISCC-CODE is not a standard ISO 24138 identifier. Off by default.
- `POST /api/v1/iscc` includes granular simprint features in the `features` field by default
    (text content; with `semantic=true` also semantic simprints). Simprints are 256-bit
    fingerprints with UTF-8 byte based offsets and sizes. Opt out per request with
    `?granular=false`.
- `POST /api/v1/simprint` generates granular simprints from plain text - byte-identical to
    [iscc-search](https://github.com/iscc/iscc-search)'s local simprint generation, so search
    services can delegate text processing to this service.

<img align="left" width="200" src="docs/assets/iscc-web-vue-frontend.jpg?raw=true">

**Demo Frontend**

The service also hosts a [Vue.js](https://vuejs.org/) based demo frontend that shows how to
upload media files, generate ISCCs, embed metadata, and compare ISCCs.<br><br><br>

## Configuration

The service is configured through `ISCC_WEB_*` environment variables and overridable ISCC
processing defaults (`ISCC_SDK_*`, `ISCC_SCT_*`, `ISCC_SCI_*`). See the
[configuration guide](https://web.iscc.codes/howto/configuration/) for the complete reference.

## Deployment

A docker-compose based standalone deployment with automatic SSL/TLS configuration is documented
in the [deployment guide](https://web.iscc.codes/howto/deployment/).

## Development

Both the backend and frontend servers need to run in parallel.

### Backend

Having [uv](https://docs.astral.sh/uv/) installed do:

```shell
git clone https://github.com/iscc/iscc-web.git
cd iscc-web
uv sync
uv run iscc-web
```

Access the app at http://localhost:8000
API documentation is at /docs

Before committing any changes run code formatting and tests with:

```
uv run poe all
```

### Frontend

Install Node.js with [asdf](https://asdf-vm.com/) or see [.tool-versions](.tool-versions) for the correct version. Packages are managed by
[pnpm](https://pnpm.io/installation).

Run `pnpm install` to install the frontend dependencies.

Run `pnpm run dev` to run the development server.

Run `pnpm run test` to run the frontend test suite (vitest).

### Documentation

The documentation site at https://web.iscc.codes is built with
[Zensical](https://zensical.org/) from the `docs/` directory. Serve it locally with
`uv run poe docs-serve` and build it with `uv run poe docs-build`. See the
[contribution guide](https://web.iscc.codes/development/contributing/) for details.

# Special thanks to the developers of

- [BlackSheep](https://github.com/Neoteroi/BlackSheep)
- [Schemathesis](https://github.com/schemathesis/schemathesis)
