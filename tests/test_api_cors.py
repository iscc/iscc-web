"""CORS tests: cross-origin API access is opt-in via ISCC_WEB_CORS_ORIGINS.

The default test server (`api` fixture) runs without CORS configuration; the secondary server
behind the `papi` fixture (see conftest.py) allows requests from tests.private_server.CORS_ORIGIN.
"""

import base64
import shutil

from httpx import codes
from iscc_samples import images

from iscc_web.options import opts
from tests.private_server import CORS_ORIGIN


def test_cors_disabled_by_default(api):
    response = api.get("/iscc/061knt35ejv6o", headers={"Origin": CORS_ORIGIN})
    assert response.status_code == codes.OK
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_allowed_origin(papi):
    headers = {
        "Origin": CORS_ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, X-Upload-Filename",
    }
    response = papi.options("/media", headers=headers)
    assert response.status_code == codes.OK
    assert response.headers["access-control-allow-origin"] == CORS_ORIGIN
    assert set(response.headers["access-control-allow-methods"].split(", ")) == {"GET", "POST", "DELETE"}
    assert response.headers["access-control-allow-headers"] == "Content-Type, X-Upload-Filename"
    assert response.headers["access-control-max-age"] == "300"


def test_cors_same_origin_always_allowed(papi):
    # Browsers send an Origin header on same-origin POST/DELETE too; the service's own origin
    # (site_address, default http://localhost:8000) must be allowed even when not listed in
    # ISCC_WEB_CORS_ORIGINS, otherwise enabling CORS breaks the bundled frontend.
    headers = {"Origin": "http://localhost:8000", "Access-Control-Request-Method": "POST"}
    response = papi.options("/media", headers=headers)
    assert response.status_code == codes.OK
    assert response.headers["access-control-allow-origin"] == "http://localhost:8000"


def test_cors_preflight_forbidden_origin(papi):
    headers = {"Origin": "https://evil.example.com", "Access-Control-Request-Method": "POST"}
    response = papi.options("/media", headers=headers)
    assert response.status_code == codes.BAD_REQUEST


def test_cors_upload_and_delete_response_headers(papi):
    content = images()[0].open("rb").read()
    headers = {
        "X-Upload-Filename": base64.b64encode(b"cors-test.jpg").decode(),
        "Origin": CORS_ORIGIN,
    }
    response = papi.post("/media", content=content, headers=headers)
    assert response.status_code == codes.CREATED
    assert response.headers["access-control-allow-origin"] == CORS_ORIGIN
    exposed = response.headers["access-control-expose-headers"]
    assert "location" in exposed
    assert "content-disposition" in exposed

    media_id = response.json()["media_id"]
    try:
        response = papi.delete(f"/media/{media_id}", headers={"Origin": CORS_ORIGIN})
        assert response.status_code == codes.NO_CONTENT
        assert response.headers["access-control-allow-origin"] == CORS_ORIGIN
    finally:
        shutil.rmtree(opts.media_path / media_id, ignore_errors=True)
