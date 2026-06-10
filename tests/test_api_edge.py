"""Edge-case tests against the live API server: upload validation, index page, explain errors."""

import base64
import shutil

import httpx
from httpx import codes
from iscc_samples import images

from iscc_web.api.mixins import FileHandler
from iscc_web.api.models import UploadMeta
from iscc_web.options import opts
from tests.conftest import server_host, server_port

FILENAME_HEADER = {"X-Upload-Filename": base64.b64encode(b"test-image.jpg").decode()}


def test_index_page():
    response = httpx.get(f"http://{server_host}:{server_port}/")
    assert response.status_code == codes.OK
    assert "<html" in response.text


def test_upload_missing_filename_header(api):
    response = api.post("/media", content=b"data")
    assert response.status_code == codes.BAD_REQUEST
    assert "Missing header" in response.text


def test_upload_filename_not_base64(api):
    response = api.post("/media", content=b"data", headers={"X-Upload-Filename": "not-base64!!!"})
    assert response.status_code == codes.BAD_REQUEST
    assert "not base64" in response.text


def test_upload_filename_not_utf8(api):
    bad = base64.b64encode(b"\xff\xfe\xfa").decode()
    response = api.post("/media", content=b"data", headers={"X-Upload-Filename": bad})
    assert response.status_code == codes.BAD_REQUEST
    assert "not UTF-8" in response.text


def test_upload_empty_body(api):
    response = api.post("/media", content=b"", headers=FILENAME_HEADER)
    assert response.status_code == codes.BAD_REQUEST


def test_upload_oversized(api):
    content = b"0" * (opts.max_upload_size + 1)
    response = api.post("/media", content=content, headers=FILENAME_HEADER)
    assert response.status_code == codes.BAD_REQUEST


def test_upload_chunked_without_content_length(api):
    content = images()[0].open("rb").read()
    response = api.post("/media", content=iter([content]), headers=FILENAME_HEADER)
    assert response.status_code == codes.CREATED
    media_id = response.json()["media_id"]
    assert api.delete(f"/media/{media_id}").status_code == codes.NO_CONTENT


def test_missing_media_file_returns_not_found(api):
    """A package whose media file vanished yields 404 on download and metadata extraction."""
    media_id = FileHandler.new_media_id()
    package = opts.media_path / media_id
    package.mkdir()
    meta = UploadMeta(media_id=media_id, file_name="gone.jpg", content_type="image/jpeg", user="0" * 64)
    (package / f"{media_id}.meta.json").write_text(meta.model_dump_json())
    try:
        assert api.get(f"/media/{media_id}").status_code == codes.NOT_FOUND
        assert api.get(f"/metadata/{media_id}").status_code == codes.NOT_FOUND
    finally:
        shutil.rmtree(package)


def test_explain_invalid_iscc(api):
    # Composite code with invalid subtype - iscc-core raises IndexError (see explain.py).
    response = api.get("/explain/KMUIV3NRGY")
    assert response.status_code == codes.BAD_REQUEST


def test_explain_invalid_length(api):
    response = api.get("/explain/ISCC:AAAAAAAAAA2")
    assert response.status_code == codes.BAD_REQUEST
