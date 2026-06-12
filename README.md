# ISCC - Generator Microservice

[![CI](https://github.com/iscc/iscc-web/actions/workflows/ci.yml/badge.svg)](https://github.com/iscc/iscc-web/actions/workflows/ci.yml)

## About `iscc-web`

`iscc-web` is a microservice for generating **International Standard Content Codes**
([ISCC](https://iscc.codes)) for media files. A public instance of this service is available at
https://iscc.io

## Overview

<img align="left" width="200" src="docs/iscc-web-rest-api.jpg?raw=true">

**REST API**

The microservice provides a REST API for generating ISCCs. The endpoints support file
upload/download, metadata extraction/embedding and ISCC processing.<br>

Files uploaded for processing are automatically deleted after a configurable timeout.
An interactive API documentation is available at [/docs](https://iscc.io/docs)<br><br>

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

<img align="left" width="200" src="docs/iscc-web-vue-frontend.jpg?raw=true">

**Demo Frontend**

The service also hosts a [Vue.js](https://vuejs.org/) based demo frontend that shows how to
upload media files, geneerate ISCCs, embed metadata, and compare ISCCs.<br><br><br>

## Configuration

Configuration is handled by environment variables:

**Backend:**

- `ISCC_WEB_ENVIRONMENT`: `development` or `production` (default: `development`).
- `ISCC_WEB_SITE_ADDRESS`: public site address (default: http://localhost:8000).
- `ISCC_WEB_PRIVATE_FILES`: restrict file downloads to original uploader (default: true).
- `ISCC_WEB_CORS_ORIGINS`: origins allowed for cross-origin API requests, space or comma
    separated (e.g. `https://app.example.com`, use `*` to allow any origin). Empty disables
    CORS support (default: empty). The service's own origin (`ISCC_WEB_SITE_ADDRESS`) is always
    allowed, so the bundled frontend keeps working. Note: with `ISCC_WEB_PRIVATE_FILES` enabled,
    uploaders are identified by client IP - make sure your reverse proxy forwards real client IPs.
- `ISCC_WEB_MAX_UPLOAD_SIZE`: max file size per file upload in bytes (default: 1073741824).
- `ISCC_WEB_STORAGE_EXPIRY`: delete uploaded files after x seconds (default 3600).
- `ISCC_WEB_CLEANUP_INTERVAL`: interval in seconds to run file cleanup task. Use 0 to deactivate (default: 600).
- `ISCC_WEB_LOG_LEVEL`: set log level (default: `DEBUG`).
- `ISCC_WEB_IO_READ_SIZE`: file read chunk size (default: 2097152).
- `ISCC_WEB_MAX_WORKERS`: max number of ISCC worker processes (default: CPU count). Each worker
    lazy-loads the iscc-sdk toolchain and - when semantic features are requested - the iscc-sct and
    iscc-sci ONNX models, which can take several hundred MB of RAM per worker. Lower this value on
    memory-constrained hosts.
- `ISCC_WEB_SENTRY_DSN`: optional sentry dsn for error reporting (default: emtpy string).

The production Dockerfile also supports `PORT` to configure gunicorns default port. (see [gunicorn
docs](https://docs.gunicorn.org/en/stable/settings.html?highlight=PORT#bind) for details)

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
Api documentation is at /docs

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

# Special thanks to the developers of

- [Blacksheep](https://github.com/Neoteroi/BlackSheep) (see [benchmarks](http://klen.github.io/py-frameworks-bench/))
- [Schemathesis](https://github.com/schemathesis/schemathesis)

## Deployment

There are many options to deploy a Python [ASGI](https://asgi.readthedocs.io/en/latest/) application.
Here is a simple docker-compose based standalone deployment with automatic SSL/TLS configuration.
Create these three files on your server:

### Caddyfile

```
{
  email {$ISCC_WEB_SITE_EMAIL}
}

{$ISCC_WEB_SITE_ADDRESS} {
  reverse_proxy app:8000
}
```

### .env

```.env
ISCC_WEB_ENVIRONMENT=production
ISCC_WEB_SITE_EMAIL=admin@example.com
ISCC_WEB_SITE_ADDRESS=https://example.com
ISCC_WEB_PRIVATE_FILES=true
ISCC_WEB_MAX_UPLOAD_SIZE=1073741824
ISCC_WEB_STORAGE_EXPIRY=3600
ISCC_WEB_CLEANUP_INTERVAL=600
ISCC_WEB_LOG_LEVEL=INFO
ISCC_WEB_IO_READ_SIZE=2097152
FORWARDED_ALLOW_IPS=*
```

The experimental Semantic-Code ISCC-UNIT is off by default and enabled per API call with
`?semantic=true`; granular fingerprints are on by default and disabled with `?granular=false`
(see [/docs](https://iscc.io/docs)). The service applies the following ISCC processing
defaults, each overridable through the corresponding environment variable:

```shell
ISCC_SDK_EXPERIMENTAL=false  # Semantic-Code ISCC-UNIT as part of the ISCC-CODE
ISCC_SDK_GRANULAR=true       # granular fingerprints for ISCC-CODEs
ISCC_SDK_BYTE_OFFSETS=true   # UTF-8 byte offsets (instead of characters) for granular features
ISCC_SDK_ADD_UNITS=true      # ISCC-UNITs in the `units` field
ISCC_SDK_BITS=256            # bit-length of ISCC-UNITs
ISCC_SDK_WIDE=true           # wide (128-bit) Data/Instance units for 2-unit ISCC-SUM
ISCC_SDK_FALLBACK=true       # ISCC-SUM fallback for unsupported media types (instead of HTTP 422)
ISCC_SCT_BITS=256            # bit-length of Semantic Text-Code units
ISCC_SCT_BITS_GRANULAR=256   # bit-length of granular semantic text simprints
ISCC_SCT_SIMPRINTS=true      # granular semantic text simprints (output only with granular=true)
ISCC_SCT_OFFSETS=true        # offsets for granular semantic text simprints
ISCC_SCT_SIZES=true          # sizes for granular semantic text simprints
ISCC_SCT_BYTE_OFFSETS=true   # UTF-8 byte offsets for granular semantic text simprints
ISCC_SCI_BITS=256            # bit-length of Semantic Image-Code units
```

Further iscc-core and iscc-sdk options can be configured through their own environment
variables:

- https://sdk.iscc.codes/options/
- https://core.iscc.codes/options/options/

### docker-compose.yaml

```yaml
version: '3.8'

volumes:
  caddy-config:
  caddy-data:

services:
  app:
    image: ghcr.io/iscc/iscc-web:main
    init: true
    env_file: .env
  caddy:
    image: caddy:2.6.1-alpine
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy-config:/config
      - caddy-data:/data
    ports:
      - 80:80
      - 443:443
      - 443:443/udp
    depends_on:
      - app
```

Make sure you have a DNS entry pointing to your servers IP and set the correct
`ISCC_WEB_SITE_ADDRESS` in your `.env` file. You should also change `ISCC_WEB_SITE_EMAIL`.

### Start the app

`docker-compose up -d`

### Watch logs

`docker-compose logs -f`

### Update to the latest docker image

```shell
docker-compose pull
docker-compose up -d
```
