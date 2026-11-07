# Changelog

## [0.4.0] - Unreleased

- Added `GET /health` (at the site root) as a readiness probe: it reports whether the
    semantic-code ONNX models are loaded, which execution provider they run on, and the image
    version and revision, and answers `503` while models load or when a GPU image's models fell
    back to CPU. Both Docker images declare a matching `HEALTHCHECK`
- All ISCC worker processes now start with the service and load the ONNX models up front instead
    of on first use, so no request waits for a model load (about 700 MB of RAM per worker on CPU;
    set `ISCC_WEB_MAX_WORKERS` on many-core hosts)
- Requires Python 3.14; the Docker images run CPython 3.14.10 (`python:3.14-slim` on Debian
    trixie for the CPU image, a uv-managed CPython on the CUDA base for the GPU image)
- Updated `iscc-sdk` to 0.9.7, `iscc-sci` to 0.4.1, `iscc-sct` to 0.2.2 and `iscc-tika` to 0.6.0;
    the `generator` field reports `iscc-sdk - v0.9.7`, and metadata embedding
    (`POST /api/v1/metadata/{media_id}`) writes slightly different file bytes, so the Data-Code,
    Instance-Code and `datahash` of embedded files change (Meta-Code and Content-Code do not)
- Updated all other backend and frontend dependencies; the frontend builds with Node.js 26 LTS
    and pnpm 12
- Builds are reproducible: Docker base images are pinned by digest, GitHub Actions by commit SHA,
    and the Python, Node.js and uv versions in `.python-version` and `.tool-versions`

## [0.3.3] - 2026-10-18

- Updated `iscc-core` to 1.5.0 and `iscc-lib` to 0.7.0 (now the minimum required versions), which
    fix Image-Codes longer than 64 bits to follow ISO 24138:2024 - the 256-bit Image-Code units
    returned with `units` change beyond the first 64 bits, while ISCC-CODEs and 64-bit units are
    unaffected
- Updated `iscc-sdk` to 0.9.6 - extracted text is no longer truncated at 500,000 characters
    (Text-Codes and granular text features change for longer documents), granular text features
    drop a final chunk shorter than the CDC minimum chunk size, M4A audio is supported, and several
    image metadata extraction fixes change the Meta-Code for affected images

## [0.3.2] - 2026-06-21

- Added `ISCC_WEB_SEMANTIC_DEFAULT` to set the backend default for the `semantic` query parameter
    on `POST /api/v1/iscc` when it is omitted (off by default), decoupled from the iscc-sdk
    `ISCC_SDK_EXPERIMENTAL` default
- Added `ISCC_WEB_UI_SEMANTIC_DEFAULT` to control the initial state of the Semantic Code toggle in
    the bundled demo frontend (on by default)
- The demo frontend now reads runtime configuration from the backend, so the Semantic Code toggle
    default and the file auto-deletion notice follow the server settings (`ISCC_WEB_UI_SEMANTIC_DEFAULT`
    and `ISCC_WEB_STORAGE_EXPIRY`) instead of hardcoded values

## [0.3.1] - 2026-06-14

- Added an opt-in GPU Docker image variant published under `-gpu` tags (`:0.3.1-gpu`,
    `:0.3-gpu`, `:main-gpu`) on a CUDA base that runs the experimental semantic codes on an
    NVIDIA GPU; the default image stays the lean CPU `python:3.13-slim` build
- Tightened client-side ISCC code input validation in the demo frontend decoder

## [0.3.0] - 2026-06-12

- Added optional semantic ISCC-UNITs for text and image content via the `semantic` query
    parameter on `POST /api/v1/iscc` (experimental 5-unit ISCC-CODE, off by default)
- Added granular content simprints to ISCC results, configurable per request via the
    `granular` query parameter (on by default)
- Added `POST /api/v1/simprint` endpoint for generating content simprints from plain text
- Added ISCC-UNIT listing (`units` field) to ISCC results
- Added wide ISCC-SUM fallback for unsupported media types instead of an error response
- Added configurable CORS support via `ISCC_WEB_CORS_ORIGINS`
- Added documentation site at https://web.iscc.codes
- Redesigned the demo frontend as an adaptive decoder canvas with media file, plain text and
    ISCC code inputs, per-unit bit visualizations and side-by-side ISCC comparison
- Unified the interactive API docs at `/docs` on Stoplight Elements
- Fixed metadata embedding when media storage and temp directory are on different drives
- Fixed 422 error responses exposing internal error details
- Updated core stack to Python 3.13, BlackSheep 2.6, iscc-sdk 0.9.3 and pydantic v2
    (breaking: responses now carry iscc-schema 0.8.0 `$schema`/`@context` URLs and a
    `generator` field; running from source requires Python >=3.13)
- Updated frontend toolchain to Node 24, pnpm, Vite 8, Vue 3.5, TypeScript and Uppy 5
- Rebuilt the Docker image on python:3.13-slim with pre-downloaded semantic models; images
    are published to ghcr.io with `main` and semver tags (no `latest` tag)
- Moved the public instance to https://web.iscc.io
- Migrated development tooling from Poetry and black to uv, ruff and prek; test coverage
    gated at 100%
- Overhauled CI/CD workflows and added Renovate dependency updates

## [0.2.0] - 2022-12-09

- Added support for pdf, epub thumbnails and metadata embedding
- Added support for audio cover art extraction
- Added support for keyword metadata field
- Updated dependencies

## [0.1.0] - 2022-11-16

- Initial release

[0.1.0]: https://github.com/iscc/iscc-web/releases/tag/v0.1.0
[0.2.0]: https://github.com/iscc/iscc-web/compare/v0.1.0...v0.2.0
[0.3.0]: https://github.com/iscc/iscc-web/compare/v0.2.0...v0.3.0
[0.3.1]: https://github.com/iscc/iscc-web/compare/v0.3.0...v0.3.1
[0.3.2]: https://github.com/iscc/iscc-web/compare/v0.3.1...v0.3.2
[0.3.3]: https://github.com/iscc/iscc-web/compare/v0.3.2...v0.3.3
[0.4.0]: https://github.com/iscc/iscc-web/compare/v0.3.3...HEAD
