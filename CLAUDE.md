# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`iscc-web` is a microservice for generating [International Standard Content Codes](https://iscc.codes) (ISCC) from media files. It combines a Python async backend (BlackSheep ASGI framework) with a Vue.js 3 frontend. A public instance runs at https://iscc.io.

## Build & Run Commands

### Backend (Python + uv)

```bash
uv sync                                 # Install dependencies
uv run pytest                           # Run all tests
uv run pytest tests/test_api_explain.py              # Run single test file
uv run pytest tests/test_api_explain.py::test_explain_iscc  # Run single test
uv run poe run                          # Dev server (uvicorn with reload)
uv run poe format                       # Format with black (line-length=100)
uv run poe test                         # Run tests via poe
uv run poe codegen                      # Regenerate schema.py from openapi.yaml
uv run poe all                          # Format OpenAPI, codegen, format, LF fix, test
```

### Frontend (Node.js + pnpm)

```bash
pnpm install                            # Install dependencies
pnpm run dev                            # Vite dev server (localhost:5173)
pnpm run build                          # Production build (outputs to iscc_web/static/dist/)
```

Both backend and frontend dev servers must run simultaneously during development. The backend serves on `:8000`, the Vite dev server on `:5173` (with HMR proxied via Jinja2 template tags).

### Linting (CI)

- **Python**: `black` (line-length 100, target py38)
- **Frontend**: `pnpm exec eslint frontend/` and `pnpm exec vue-tsc --noEmit`
- **Docker**: hadolint
- **Shell**: shellcheck

## Architecture

### Backend (`iscc_web/`)

Built on [BlackSheep](https://github.com/Neoteroi/BlackSheep), an async ASGI web framework. Key dependencies: `iscc-sdk`, `iscc-core`.

- **`main.py`** - Application entrypoint. Creates the `Application` instance, configures Jinja2 rendering, static file serving, route patterns, and lifecycle hooks (logging, cleanup, shutdown). Entry point: `main()` runs uvicorn; ASGI: `iscc_web.main:app`.
- **`options.py`** - Configuration via `pydantic-settings` (`IsccWebOptions`). All settings use `ISCC_WEB_` env prefix. The singleton `opts` is imported everywhere.
- **`cleanup.py`** - Background async task that periodically deletes expired upload packages from `media/`.
- **`vite.py`** - Jinja2 extensions (`{% vite_hmr_client %}`, `{% vite_asset %}`) for Vite integration. In dev mode, tags point to the Vite dev server; in production, they read from `manifest.json`.
- **`__init__.py`** - Wildcard imports all API controllers and common utilities. This triggers BlackSheep's auto-discovery of `ApiController` subclasses.

### API Controllers (`iscc_web/api/`)

All controllers extend `ApiController` and are versioned at `v1` (routes: `/api/v1/...`). Controllers that handle file uploads also mix in `FileHandler`.

- **`iscc.py`** (`Iscc`) - `POST /iscc` uploads a file and returns its ISCC-CODE. `GET /iscc/{media_id}` retrieves a cached result.
- **`media.py`** (`Media`) - `POST /media` uploads files, `GET /media/{media_id}` downloads, `DELETE /media/{media_id}` deletes.
- **`metadata.py`** (`Metadata`) - `GET /metadata/{media_id}` extracts metadata, `POST /metadata/{media_id}` embeds metadata and reprocesses ISCC.
- **`explain.py`** (`Explain`) - `GET /explain/{iscc}` decomposes an ISCC into units with various representations.
- **`mixins.py`** (`FileHandler`) - Shared file handling logic: upload processing, media package management (create/read/write/delete), ISCC processing via `ProcessPoolExecutor`.
- **`pool.py`** (`Pool`) - `ProcessPoolExecutor` wrapper registered as a singleton service. Auto-recovers from `BrokenProcessPool`.
- **`schema.py`** - **Auto-generated** from `openapi.yaml` by `datamodel-codegen`. Do not edit manually; run `poe codegen` to regenerate.
- **`models.py`** - `UploadMeta` pydantic model for file upload metadata.

### Media Package Convention

Each uploaded file gets a unique `media_id` (13-char Flake ID). Files are stored in `media/{media_id}/` alongside `{media_id}.meta.json` (upload metadata) and `{media_id}.iscc.json` (ISCC result).

### Frontend (`frontend/`)

Vue.js 3 SPA with TypeScript, built with Vite. Uses Pug templates, Bootstrap 5, and SCSS.

- **`App.vue`** - Main app component
- **`components/`** - `UploadZone.vue`, `UploadedFile.vue`, `IsccHeader.vue`, `IsccFooter.vue`
- **`services/api.service.ts`** - API client
- **`vite.config.ts`** - Vite config. Build output goes to `iscc_web/static/dist/`. Manifest-based asset resolution for production.

### OpenAPI Schema

The API is defined in `iscc_web/static/docs/openapi.yaml`. Interactive docs are served at `/docs`. The schema drives both `schema.py` code generation and schemathesis-based fuzz testing.

### Test Architecture

Tests spin up a real server process (uvicorn on port 44555) via a session-scoped fixture and make HTTP requests with `httpx.Client`. The `iscc-samples` package provides test media files. Schemathesis runs stateful API fuzz tests against the OpenAPI spec.

## Modernization Status

The project is mid-migration:
- BlackSheep is being upgraded to a major version (see `docs/blacksheep-changelog.md` for API changes)
- Python version constraint in `pyproject.toml` (`>=3.10,<3.12`) and CI (3.11) differ from `.tool-versions` (3.9.14) - the newer versions are the target
- Several dependency versions in `pyproject.toml` are pinned to old ranges and being updated
- The `asgi.py` module referenced by `poe run` does not exist yet

## Docker

Multi-stage Dockerfile: Python builder, Node.js frontend builder, slim runtime. Production uses gunicorn with uvicorn workers. Image published to `ghcr.io/iscc/iscc-web`.
