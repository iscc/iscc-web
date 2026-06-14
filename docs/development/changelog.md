---
# Generated from CHANGELOG.md by develop/copy_changelog.py - do not edit.
icon: lucide/history
description: Release history of the iscc-web microservice.
---

# Changelog

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
- Addded support for keyword metadata field
- Updated dependencies

## [0.1.0] - 2022-11-16

- Initial release

[0.1.0]: https://github.com/iscc/iscc-web/releases/tag/v0.1.0
[0.2.0]: https://github.com/iscc/iscc-web/compare/v0.1.0...v0.2.0
[0.3.0]: https://github.com/iscc/iscc-web/compare/v0.2.0...v0.3.0
