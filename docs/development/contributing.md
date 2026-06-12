---
icon: lucide/git-pull-request
description: Developer setup for backend and frontend, integration tests with a 100% coverage gate, linting, prek hooks, and docs builds.
---

# Contributing

## Dev environment setup

`iscc-web` has two parts: a Python backend and a Vue 3 frontend. During development both dev
servers run in parallel — with `ISCC_WEB_ENVIRONMENT=development` (the default) the backend's page
template loads frontend assets from the Vite dev server, so you get hot module replacement while
working against the real API.

### Backend

1. Clone the repository:

    ```bash
    git clone https://github.com/iscc/iscc-web.git
    cd iscc-web
    ```

1. Install dependencies with [uv](https://docs.astral.sh/uv/) (the Python version is pinned in
    `.python-version`):

    ```bash
    uv sync
    ```

1. Run the dev server (auto-reload enabled in development):

    ```bash
    uv run iscc-web
    ```

    The app is served at http://localhost:8000 and the interactive API docs at
    http://localhost:8000/docs.

### Frontend

1. Install Node.js — the required version is listed in `.tool-versions` (for example via
    [asdf](https://asdf-vm.com/)). The matching [pnpm](https://pnpm.io/) version is pinned in the
    `packageManager` field of `package.json`.

1. Install dependencies and start the Vite dev server:

    ```bash
    pnpm install
    pnpm run dev
    ```

    Vite serves frontend assets on port 5173. Keep browsing the app through the backend at
    http://localhost:8000 — its template injects script tags pointing at the Vite dev server.

## Running tests

The backend test suite requires 100% branch coverage (`fail_under` in `pyproject.toml`). Run the
full suite in parallel with coverage:

```bash
uv run poe test
```

These are integration tests: `tests/conftest.py` boots a real uvicorn server in a subprocess and
the tests exercise it over HTTP with httpx — no mocks. The server subprocess is measured by
coverage too, so it must always shut down gracefully.

Run a single test file or function (without xdist and coverage):

```bash
uv run pytest tests/test_api_iscc.py
uv run pytest tests/test_api_iscc.py::test_get_iscc_ok
```

## Frontend tests

```bash
pnpm run test                # vitest component/unit tests (jsdom + @vue/test-utils)
pnpm exec eslint frontend/   # lint
pnpm exec vue-tsc --noEmit   # type check
```

CI runs all three plus `pnpm run build`.

## Linting and formatting

```bash
uv run poe format
```

This runs `ruff format`. The max line length is 120 characters and line endings are LF, both
configured in `pyproject.toml`. Ruff linting runs as part of the prek hooks below.

## prek hooks

Git hooks are defined in `.pre-commit-config.yaml` and run with
[prek](https://github.com/j178/prek), a pre-commit-compatible runner. One-time setup:

```bash
uv run prek install
```

Run all hooks against the whole repository:

```bash
uv run prek run --all-files
```

The hooks cover whitespace/end-of-file/LF fixers, JSON/TOML/YAML checks, ruff format + lint,
mdformat for Markdown, and `openapi-spec-validator` for `iscc_web/static/docs/openapi.yaml`.

## Before committing

Run the catch-all quality gate:

```bash
uv run poe all
```

It runs the following tasks in sequence:

| Task               | What it does                                               |
| ------------------ | ---------------------------------------------------------- |
| `formatopenapi`    | Reformats `iscc_web/static/docs/openapi.yaml`              |
| `codegen`          | Regenerates `iscc_web/api/schema.py` from the OpenAPI spec |
| `format`           | Formats code with ruff                                     |
| `test`             | Runs the test suite with the 100% coverage gate            |
| `check-complexity` | Checks cyclomatic complexity with radon                    |

!!! warning "Never edit `schema.py` by hand"

    `iscc_web/api/schema.py` is generated from `openapi.yaml` — the spec is the source of truth
    for the [REST API](../reference/rest-api.md). Edit the yaml and run `uv run poe codegen`. See
    [Architecture](../explanation/architecture.md) for how the OpenAPI-first layer fits together.

## Documentation

Serve the docs locally with live reload:

```bash
uv run poe docs-serve
```

Build for deployment — this builds the static site with [Zensical](https://zensical.org/) into
`site/` and generates `llms-full.txt` for LLM consumption:

```bash
uv run poe docs-build
```

## Cross-platform support

All code, scripts, and dev tools must work on **Linux**, **macOS**, and **Windows**. Please test on
multiple platforms when possible.
