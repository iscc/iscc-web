# Baseline status before v0.3.0 modernization (Stage 0)

Recorded 2026-06-10 on Windows 10, prior to any toolchain or code changes (tree at
`b5e42ca`).

## Test suite

- Interpreter: Python 3.9.25 (uv-managed; `.tool-versions` pins 3.9.14)
- Installer: Poetry 1.2.1 run via `uvx --prerelease=allow --python 3.9 --from "poetry==1.2.1"`
    (Poetry 2.x cannot read the lock-version 1.1 `poetry.lock`; Poetry 1.2.1 itself needs
    `--prerelease=allow` because its `cleo` dependency resolves to a yanked release)
- `poetry install` succeeded with all 121 locked packages; Python 3.10 is NOT viable for the
    baseline (PyYAML 5.4.1 has no cp310 wheels and its sdist no longer builds under Cython 3)
- Result: **16 passed in 36.77s** — zero failures

Collected tests:

```
tests/test_api_explain.py::test_explain_iscc
tests/test_api_iscc.py::test_create_iscc_location_and_result
tests/test_api_iscc.py::test_get_iscc_ok
tests/test_api_iscc.py::test_get_iscc_not_found
tests/test_api_media.py::test_upload_and_delete_file
tests/test_api_media.py::test_download_missing
tests/test_api_metadata.py::test_upload_extract_embed_download
tests/test_api_schemathesis.py::test_api[POST /api/v1/iscc]
tests/test_api_schemathesis.py::test_api[GET /api/v1/iscc/{media_id}]
tests/test_api_schemathesis.py::test_api[POST /api/v1/media]
tests/test_api_schemathesis.py::test_api[GET /api/v1/media/{media_id}]
tests/test_api_schemathesis.py::test_api[DELETE /api/v1/media/{media_id}]
tests/test_api_schemathesis.py::test_api[GET /api/v1/metadata/{media_id}]
tests/test_api_schemathesis.py::test_api[POST /api/v1/metadata/{media_id}]
tests/test_api_schemathesis.py::test_api[GET /api/v1/explain/{iscc}]
tests/test_iscc_web.py::test_version
```

## Behavior quirks worth preserving through the migration

- Uploads are raw request bodies (NOT multipart); the filename travels as a base64-encoded
    `X-Upload-Filename` header. `POST /api/v1/media` returns 201 with a `Location` header.
- Each upload creates a package dir `media/{media_id}/` with the file plus
    `{media_id}.meta.json` and `{media_id}.iscc.json`; media IDs are lowercased iscc-core
    Flake codes.
- Privacy model: the "user" is the blake3 hash of the client IP; with
    `ISCC_WEB_PRIVATE_FILES` (default true) download/delete/embed are uploader-only (403 for
    others).
- `media/061knt35ejv6o` is a permanent fixture skipped by `cleanup.py`; tests depend on it.
- Tests are integration tests against a real uvicorn server (subprocess, port 44555,
    session-scoped autouse fixture); many assert full JSON responses including exact ISCC
    values and `$schema`/`@context` URLs (these change with iscc-sdk/iscc-schema bumps).
- Schemathesis property tests run against `iscc_web/static/docs/openapi.yaml`, so spec and
    implementation must stay in sync.
