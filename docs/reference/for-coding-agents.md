---
icon: lucide/bot
description: Prescriptive reference for AI coding agents — API contracts, architecture map, commands, invariants, and change playbooks.
---

# For Coding Agents

Dense, prescriptive reference for AI agents integrating with the `iscc-web` REST API or working on
the codebase. Tables and code over prose. Terminology matches the codebase exactly.

## Integrating with the API

Base path: `/api/v1` (public instance: `https://iscc.io/api/v1`). The OpenAPI spec is served at
`/docs/openapi.yaml` with interactive docs at `/docs`. Full details:
[REST API reference](rest-api.md).

### Endpoints

| Method   | Path                        | Purpose                                                | Success |
| -------- | --------------------------- | ------------------------------------------------------ | ------- |
| `POST`   | `/iscc?semantic=&granular=` | Upload file and generate its ISCC                      | `201`   |
| `GET`    | `/iscc/{media_id}`          | Stored ISCC result for a previous upload               | `200`   |
| `POST`   | `/media`                    | Upload file without ISCC processing                    | `201`   |
| `GET`    | `/media/{media_id}`         | Download uploaded file (uploader-only\*)               | `200`   |
| `DELETE` | `/media/{media_id}`         | Delete media package (uploader-only\*)                 | `204`   |
| `GET`    | `/metadata/{media_id}`      | Extract embedded metadata                              | `200`   |
| `POST`   | `/metadata/{media_id}`      | Embed metadata into a copy + re-ISCC (uploader-only\*) | `201`   |
| `GET`    | `/explain/{iscc}`           | Decompose an ISCC into its units                       | `200`   |
| `POST`   | `/simprint`                 | Granular simprints from plain text (JSON body)         | `200`   |

\* With `ISCC_WEB_PRIVATE_FILES=true` (the default) these return `403` unless the request comes
from the original uploader's IP (identified by its blake3 hash — no raw IPs are stored).

Path parameter handling:

| Parameter  | Validation                                                                      | On failure |
| ---------- | ------------------------------------------------------------------------------- | ---------- |
| `media_id` | Routing layer: `{mid:media_id}` pattern `[a-v0-9]{13}$` (lowercased Flake code) | `404`      |
| `iscc`     | Handler: `ic.iscc_normalize` + `ic.iscc_validate` (`ISCC:` prefix optional)     | `400`      |

The `iscc` entry in `Route.value_patterns` (`iscc_web/main.py`) is registered but unused — the
explain route declares a bare `{iscc}` parameter, so no routing-level pattern applies to it.

### Upload contract

Uploads are **raw request bodies — not multipart forms**. The filename travels base64-encoded in
the `X-Upload-Filename` header. Applies to `POST /iscc` and `POST /media`.

| Rule                | Detail                                                                                    |
| ------------------- | ----------------------------------------------------------------------------------------- |
| Body                | Raw file bytes (`application/octet-stream` semantics)                                     |
| `X-Upload-Filename` | Required. Base64 of the UTF-8 filename. Missing, invalid base64, or invalid UTF-8 → `400` |
| `Content-Type`      | Optional. Stored as upload metadata and replayed on download                              |
| `Content-Length`    | Must be ≥ 1 and ≤ `ISCC_WEB_MAX_UPLOAD_SIZE` (default 1 GB), else `400`                   |
| Response            | `201` with `Location: /api/v1/media/{media_id}` and an ISCC metadata JSON body            |

=== "Python (httpx)"

    ```python
    import base64
    import httpx

    filename = "your-media-file.jpg"
    headers = {
        "X-Upload-Filename": base64.b64encode(filename.encode("utf-8")).decode("ascii"),
        "Content-Type": "image/jpeg",
    }
    with open(filename, "rb") as f:
        response = httpx.post(
            "https://iscc.io/api/v1/iscc",
            params={"semantic": "false", "granular": "true"},
            content=f.read(),  # raw body, NOT files={...}
            headers=headers,
            timeout=None,
        )
    response.raise_for_status()
    result = response.json()
    print(result["iscc"], response.headers["location"])
    ```

=== "curl"

    ```shell
    curl -X POST "https://iscc.io/api/v1/iscc?semantic=false&granular=true" \
      --data-binary @your-media-file.jpg \
      -H "X-Upload-Filename: $(printf %s "your-media-file.jpg" | base64)" \
      -H "Content-Type: image/jpeg"
    ```

### API behaviors to plan around

- `semantic`/`granular` omitted on `POST /iscc` → service defaults apply (semantic off, granular
    on, via `ISCC_SDK_EXPERIMENTAL`/`ISCC_SDK_GRANULAR`); explicit values override per request.
    `semantic=true` yields a 5-unit ISCC-CODE that is **not** a standard ISO 24138 identifier.
- `POST /metadata/{media_id}` has no `semantic` param — it reprocesses with service defaults, so
    embedding into a 5-unit result returns a 4-unit code.
- Unsupported media types do not fail: they yield a 2-unit wide ISCC-SUM (Data + Instance)
    because `ISCC_SDK_FALLBACK=true` is the service default.
- Uploads are ephemeral: a cleanup task deletes media packages older than
    `ISCC_WEB_STORAGE_EXPIRY` (default 3600 s). Persist the `201` response JSON.
- CORS is disabled by default; set `ISCC_WEB_CORS_ORIGINS` for cross-origin clients
    (see [Configuration](../howto/configuration.md)).

## Working on the codebase

### Architecture map

| File                                | Contains                                                                                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `iscc_web/__init__.py`              | Star imports that register all controllers as an import side effect — routing depends on this                                                                |
| `iscc_web/main.py`                  | BlackSheep `Application`, CORS setup, static file serving, `Route.value_patterns` (`mid`, `iscc`), cleanup-task startup, `Pool` shutdown, uvicorn `main()`   |
| `iscc_web/asgi.py`                  | ASGI entrypoint for the uvicorn dev server                                                                                                                   |
| `iscc_web/options.py`               | `IsccWebOptions` (pydantic-settings, `ISCC_WEB_` prefix); `ISCC_LIB_ENV_DEFAULTS` applied via `os.environ.setdefault` before the iscc libraries are imported |
| `iscc_web/cleanup.py`               | `cleanup_task()` — deletes expired media packages; skips `061knt35ejv6o` and `.gitignore`                                                                    |
| `iscc_web/vite.py`                  | Jinja2 tags `{% vite_hmr_client %}` / `{% vite_asset %}`; Vite manifest resolution in production                                                             |
| `iscc_web/api/iscc.py`              | `Iscc` controller — `POST /iscc`, `GET /iscc/{media_id}`                                                                                                     |
| `iscc_web/api/media.py`             | `Media` controller — `POST /media`, `GET`/`DELETE /media/{media_id}`                                                                                         |
| `iscc_web/api/metadata.py`          | `Metadata` controller — `GET`/`POST /metadata/{media_id}`                                                                                                    |
| `iscc_web/api/explain.py`           | `Explain` controller — `GET /explain/{iscc}` (with iscc-core `IndexError` workaround)                                                                        |
| `iscc_web/api/simprint.py`          | `Simprint` controller — `POST /simprint`; `text_simprints()` (byte-identical to iscc-search)                                                                 |
| `iscc_web/api/mixins.py`            | `FileHandler` — shared upload/storage logic; `code_iscc()` pool wrapper                                                                                      |
| `iscc_web/api/pool.py`              | `Pool` — `ProcessPoolExecutor` wrapper, self-healing on `BrokenProcessPool`                                                                                  |
| `iscc_web/api/schema.py`            | **Generated** pydantic models from `openapi.yaml` — never edit by hand                                                                                       |
| `iscc_web/api/models.py`            | `UploadMeta` — internal upload metadata model (hand-written)                                                                                                 |
| `iscc_web/api/common.py`            | `rmtree`, `base_url` helpers                                                                                                                                 |
| `iscc_web/static/docs/openapi.yaml` | API source of truth; served at `/docs`                                                                                                                       |
| `iscc_web/templates/index.jinja`    | Frontend host page (Vite asset tags)                                                                                                                         |
| `frontend/`                         | Vue 3 + TypeScript demo SPA; the API boundary is `frontend/services/api.service.ts`                                                                          |
| `tests/conftest.py`                 | Session-scoped uvicorn server subprocess (port 44555 + xdist worker offset)                                                                                  |

### Commands

Backend (uv; Python version pinned in `.python-version`):

| Command                                                  | Purpose                                                                                      |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `uv sync`                                                | Install backend dependencies into `.venv`                                                    |
| `uv run iscc-web`                                        | Dev server at `http://localhost:8000` (auto-reload)                                          |
| `uv run poe all`                                         | `formatopenapi` + `codegen` + `format` + `test` + `check-complexity` — run before committing |
| `uv run poe test`                                        | `pytest -n auto` with the 100% branch-coverage gate                                          |
| `uv run pytest tests/test_api_iscc.py::test_get_iscc_ok` | Single test (no xdist, no coverage)                                                          |
| `uv run poe codegen`                                     | Regenerate `iscc_web/api/schema.py` from `openapi.yaml`                                      |
| `uv run poe formatopenapi`                               | Reformat `openapi.yaml`                                                                      |
| `uv run poe format`                                      | `ruff format` (line-length 120, LF line endings)                                             |
| `uv run prek run --all-files`                            | Pre-commit hooks (ruff, mdformat, openapi-spec-validator, ...)                               |

Frontend (pnpm; Node version pinned in `.tool-versions`):

| Command                      | Purpose                                                   |
| ---------------------------- | --------------------------------------------------------- |
| `pnpm install`               | Install frontend dependencies                             |
| `pnpm run dev`               | Vite dev server on port 5173                              |
| `pnpm run build`             | `vue-tsc` type check + build into `iscc_web/static/dist/` |
| `pnpm run test`              | Vitest unit/component tests                               |
| `pnpm exec eslint frontend/` | Lint (CI parity)                                          |
| `pnpm exec vue-tsc --noEmit` | Type check (CI parity)                                    |

### Environment variables

All service options use the `ISCC_WEB_` prefix (`iscc_web/options.py`). Quick table — full
reference in [Configuration](../howto/configuration.md):

| Variable                    | Default                     | Purpose                                                      |
| --------------------------- | --------------------------- | ------------------------------------------------------------ |
| `ISCC_WEB_ENVIRONMENT`      | `development`               | `development` enables debug details + Vite dev-server assets |
| `ISCC_WEB_SITE_ADDRESS`     | `http://localhost:8000`     | Public site address; dev server bind host/port               |
| `ISCC_WEB_MEDIA_PATH`       | `media/` beside the package | Storage directory for media packages                         |
| `ISCC_WEB_MAX_WORKERS`      | CPU count                   | ISCC worker processes (memory-heavy per worker)              |
| `ISCC_WEB_MAX_UPLOAD_SIZE`  | `1073741824`                | Max upload size in bytes                                     |
| `ISCC_WEB_IO_READ_SIZE`     | `2097152`                   | File read chunk size in bytes                                |
| `ISCC_WEB_PRIVATE_FILES`    | `true`                      | Restrict download/delete/embed to uploader                   |
| `ISCC_WEB_CORS_ORIGINS`     | *(empty)*                   | CORS origins; empty disables CORS                            |
| `ISCC_WEB_STORAGE_EXPIRY`   | `3600`                      | Seconds until uploads are deleted                            |
| `ISCC_WEB_CLEANUP_INTERVAL` | `600`                       | Cleanup interval in seconds; `0` deactivates                 |
| `ISCC_WEB_LOG_LEVEL`        | `DEBUG`                     | Loguru log level                                             |
| `ISCC_WEB_SENTRY_DSN`       | *(empty)*                   | Optional Sentry DSN                                          |

### Constraints and invariants

- `iscc_web/api/schema.py` is **generated** by datamodel-code-generator from
    `iscc_web/static/docs/openapi.yaml` (config: `[tool.datamodel-codegen]` in `pyproject.toml`).
    Edit the yaml, then `uv run poe codegen`. The file is omitted from coverage.
- Controllers are registered as an import side effect: a controller module not star-imported in
    `iscc_web/__init__.py` is **not routed** (hence the `F403` ruff ignore for that file).
- `openapi.yaml` and the implementation must stay in sync — `tests/test_api_schemathesis.py`
    runs property-based tests against the spec.
- `media/061knt35ejv6o` is a permanent fixture: `cleanup.py` skips it and tests assert its exact
    stored content. Never delete it.
- Coverage is gated at 100% with branch coverage (`fail_under` in `pyproject.toml`). The test
    server subprocess is measured too (`concurrency = ["thread", "multiprocessing"]`).
- Tests run against a real uvicorn server subprocess (spawn context, port 44555 + xdist offset) —
    no mocks. It shuts down gracefully via a multiprocessing `Event`; `terminate()` discards
    coverage data and leaks pool worker processes.
- Callables submitted to `Pool` must be picklable top-level functions (`code_iscc`,
    `text_simprints`, `idk.extract_metadata`, `idk.embed_metadata`).
- `iscc_web/options.py` must be imported before `iscc_sdk`/`iscc_sct`/`iscc_sci` — it seeds their
    environment defaults at import time, and pool workers inherit them.
- Style: ruff with line-length 120, LF line endings, target py313; prek hooks enforce
    whitespace/EOL fixes, mdformat for Markdown, and openapi-spec-validator for the spec.
- Renovate ignores `iscc-tika` (`renovate.json` `ignoreDeps`) — it must stay `<0.5.0`.

### Change playbook

#### Add an endpoint

1. Edit `iscc_web/static/docs/openapi.yaml` (path + schemas), then `uv run poe formatopenapi`.
1. `uv run poe codegen` — regenerates `iscc_web/api/schema.py`.
1. Implement an `APIController` subclass in `iscc_web/api/` (class name becomes the route
    segment; `version()` returns `"v1"`).
1. Star-import the new module in `iscc_web/__init__.py` — without this the routes do not exist.
1. Add integration tests in `tests/` (they call the live server over httpx).
1. `uv run poe all` — schemathesis validates spec conformance; coverage must stay at 100%.

#### Add a configuration option

1. Add a field to `IsccWebOptions` in `iscc_web/options.py` (env name = `ISCC_WEB_` + field name).
1. Cover it in `tests/test_options.py`. Note: `opts` is instantiated at import time — test
    servers configure the environment before importing `iscc_web` (see `tests/conftest.py`).
1. Document it in `README.md` and [Configuration](../howto/configuration.md).

#### Bump iscc-sdk / iscc-schema / iscc-core

- Expect every exact ISCC fixture assertion in `tests/` to change: ISCC values, `units`,
    `datahash`/`metahash`, the `generator` string (`iscc-sdk - vX.Y.Z`), and the
    `$schema`/`@context` URLs.
- Update the stored fixture files under `media/061knt35ejv6o/` and example values in
    `openapi.yaml` if response content changes.
- The Dockerfile pre-downloads the iscc-sct/iscc-sci ONNX models and runs `iscc-sdk install`;
    CI caches the models — check both if model handling changes.

#### Change upload handling

- `FileHandler.handle_upload()` in `iscc_web/api/mixins.py` is shared by `POST /iscc` and
    `POST /media` — both endpoints change together. Update both paths in `openapi.yaml`.

#### Change the frontend

- The SPA talks to the backend only through `frontend/services/api.service.ts`; tests live in
    `frontend/tests/`. The build writes `iscc_web/static/dist/manifest.json`, which
    `iscc_web/vite.py` resolves in production.

### Common mistakes

**NEVER** hand-edit `iscc_web/api/schema.py`. It is generated and will be overwritten.

```shell
# WRONG: edit iscc_web/api/schema.py directly
# CORRECT: edit iscc_web/static/docs/openapi.yaml, then:
uv run poe codegen
```

---

**NEVER** send uploads as `multipart/form-data`. The API reads the raw request body and takes the
filename from the base64-encoded `X-Upload-Filename` header.

---

**NEVER** delete `media/061knt35ejv6o`. It is a permanent test fixture that `cleanup.py`
deliberately skips.

---

**NEVER** `terminate()` the test server subprocess. Signal its multiprocessing `Event` and
`join()` it — otherwise coverage data is discarded and pool workers leak.

---

**NEVER** add a controller without star-importing its module in `iscc_web/__init__.py`. It will
import fine, pass type checks, and silently never be routed.

---

**NEVER** pass lambdas, closures, or instance methods to the process `Pool`. Worker submissions
must pickle; use top-level module functions.

---

**ALWAYS** import `iscc_web.options` (or `iscc_web`) before `iscc_sdk`, `iscc_sct`, or `iscc_sci`
in new modules and scripts — the service's library defaults are applied to the environment when
`options.py` is imported.

---

**ALWAYS** run `uv run poe all` before committing. It reformats the spec, regenerates the schema,
formats code, runs the full test suite with the coverage gate, and checks complexity.
