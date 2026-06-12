---
icon: lucide/settings
description: Configure iscc-web through ISCC_WEB_* environment variables and tune the ISCC processing defaults.
---

# Configuration

`iscc-web` is configured entirely through environment variables. Options are defined with
[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) in
`iscc_web/options.py` and read once at process start — restart the service to apply changes.

All service options use the `ISCC_WEB_` prefix. Variable names are case-insensitive, and boolean
options accept the usual pydantic spellings (`true`/`false`, `1`/`0`).

## Option reference

| Variable                    | Type   | Default                                | Description                                                                                                                   |
| --------------------------- | ------ | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `ISCC_WEB_ENVIRONMENT`      | string | `development`                          | `development` or `production`. Development enables debug error details and resolves frontend assets from the Vite dev server. |
| `ISCC_WEB_SITE_ADDRESS`     | URL    | `http://localhost:8000`                | Public site address. The dev server binds to its host/port; its origin is always CORS-allowed.                                |
| `ISCC_WEB_MEDIA_PATH`       | path   | `media/` beside the `iscc_web` package | Directory for uploaded media packages (one subdirectory per upload).                                                          |
| `ISCC_WEB_MAX_WORKERS`      | int    | CPU count                              | Max number of ISCC worker processes. See [Worker processes](#worker-processes-and-memory).                                    |
| `ISCC_WEB_MAX_UPLOAD_SIZE`  | int    | `1073741824`                           | Max file size per upload in bytes (1 GB).                                                                                     |
| `ISCC_WEB_IO_READ_SIZE`     | int    | `2097152`                              | File read chunk size in bytes (2 MB).                                                                                         |
| `ISCC_WEB_PRIVATE_FILES`    | bool   | `true`                                 | Restrict file download/delete/embed to the original uploader. See [Private files](#private-files).                            |
| `ISCC_WEB_CORS_ORIGINS`     | string | *(empty)*                              | Origins allowed for cross-origin API requests. Empty disables CORS. See [CORS origins](#cors-origins).                        |
| `ISCC_WEB_STORAGE_EXPIRY`   | int    | `3600`                                 | Seconds after which uploaded files are deleted.                                                                               |
| `ISCC_WEB_CLEANUP_INTERVAL` | int    | `600`                                  | Interval in seconds for the file cleanup task. `0` deactivates cleanup.                                                       |
| `ISCC_WEB_LOG_LEVEL`        | string | `DEBUG`                                | Logging level (loguru level name, e.g. `INFO`).                                                                               |
| `ISCC_WEB_SENTRY_DSN`       | string | *(empty)*                              | Optional Sentry DSN for error reporting.                                                                                      |

## CORS origins

`ISCC_WEB_CORS_ORIGINS` enables cross-origin API access for frontends hosted on other domains.
Origins are space- or comma-separated; use `*` to allow any origin:

```shell
ISCC_WEB_CORS_ORIGINS="https://app.example.com https://other.example.org"
```

When set, the CORS policy allows the `GET`, `POST` and `DELETE` methods, accepts the
`Content-Type` and `X-Upload-Filename` request headers (required for uploads — see the
[REST API reference](../reference/rest-api.md)), and exposes the `Location` and
`Content-Disposition` response headers so cross-origin clients can read upload locations and
download filenames.

The service's own origin (derived from `ISCC_WEB_SITE_ADDRESS`) is always allowed in addition to
the configured list, so the bundled demo frontend keeps working. An empty value (the default)
disables CORS support entirely.

## Private files

With `ISCC_WEB_PRIVATE_FILES=true` (the default), the service identifies each uploader by the
blake3 hash of the client IP address and stores that hash with the upload metadata. The following
operations are then restricted to the original uploader:

- `GET /api/v1/media/{media_id}` — file download
- `DELETE /api/v1/media/{media_id}` — file deletion
- `POST /api/v1/metadata/{media_id}` — metadata embedding

Requests from a different IP receive `403 Forbidden`. No raw IP addresses are persisted — only
the hash.

!!! warning "Reverse proxies must forward real client IPs"

    Behind a reverse proxy, make sure the proxy forwards real client IPs and that the ASGI server
    trusts the forwarding headers (e.g. `FORWARDED_ALLOW_IPS=*` for gunicorn/uvicorn, as in the
    [deployment example](deployment.md)). Otherwise every client appears to be the proxy's IP and
    all uploads become accessible to everyone.

## Worker processes and memory

CPU-bound ISCC processing runs in a `ProcessPoolExecutor` with `ISCC_WEB_MAX_WORKERS` worker
processes (default: CPU count). Each worker lazy-loads the iscc-sdk toolchain and — when semantic
features are requested — the iscc-sct and iscc-sci ONNX models, which can take several hundred MB
of RAM per worker.

Lower this value on memory-constrained hosts:

```shell
ISCC_WEB_MAX_WORKERS=2
```

## Storage expiry and cleanup

Uploaded files are temporary. A background task runs every `ISCC_WEB_CLEANUP_INTERVAL` seconds
and deletes every media package whose directory is older than `ISCC_WEB_STORAGE_EXPIRY` seconds
(measured from directory creation time). Two consequences of this interplay:

- A package can outlive its expiry by up to one cleanup interval. With the defaults (expiry 3600,
    interval 600), files are removed between 60 and 70 minutes after upload.
- Setting `ISCC_WEB_CLEANUP_INTERVAL=0` deactivates cleanup entirely — uploaded files are then
    kept indefinitely.

## ISCC processing defaults

The service configures the underlying ISCC libraries (iscc-sdk, iscc-sct, iscc-sci) by setting
environment defaults before those libraries are imported. Worker processes inherit them, and any
of these variables you set explicitly takes precedence over the service default:

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

### Per-request overrides

Two of these defaults can be overridden per request on `POST /api/v1/iscc`:

| Query parameter | Service default         | Effect                                                                                                                   |
| --------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `semantic`      | `ISCC_SDK_EXPERIMENTAL` | Adds an experimental Semantic-Code ISCC-UNIT to the composite ISCC-CODE (5 units — not a standard ISO 24138 identifier). |
| `granular`      | `ISCC_SDK_GRANULAR`     | Includes granular simprint features in the `features` field.                                                             |

Omitted query parameters resolve to the corresponding environment default; explicit values
override it for that request only. See the [REST API reference](../reference/rest-api.md) for
details.

### Further library options

iscc-sdk and iscc-core expose additional options through their own environment variables:

- <https://sdk.iscc.codes/options/>
- <https://core.iscc.codes/options/options/>

## Docker image port

The production Docker image (`ghcr.io/iscc/iscc-web`) runs gunicorn and additionally honors the
standard `PORT` environment variable for its bind address (default `8000`). See the
[gunicorn bind setting](https://docs.gunicorn.org/en/stable/settings.html#bind) and the
[deployment guide](deployment.md).
