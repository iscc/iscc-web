"""Private-files mode tests: download/delete/embed are restricted to the original uploader.

The server behind the `papi` fixture (see conftest.py) runs with ISCC_WEB_PRIVATE_FILES=true.
"""

import base64
import shutil

from httpx import codes
from iscc_samples import images

from iscc_web.api.mixins import FileHandler
from iscc_web.api.models import UploadMeta
from iscc_web.options import opts


def _upload(papi):
    content = images()[0].open("rb").read()
    headers = {"X-Upload-Filename": base64.b64encode(b"test-image.jpg").decode()}
    response = papi.post("/media", content=content, headers=headers)
    assert response.status_code == codes.CREATED
    return response.json()["media_id"]


def _foreign_package(file_name="foreign.jpg"):
    """Create a package on disk owned by a different (fake) user."""
    media_id = FileHandler.new_media_id()
    package = opts.media_path / media_id
    package.mkdir()
    meta = UploadMeta(media_id=media_id, file_name=file_name, content_type="image/jpeg", user="0" * 64)
    (package / f"{media_id}.meta.json").write_text(meta.model_dump_json())
    (package / file_name).write_bytes(b"foreign data")
    return media_id


def test_owner_can_download_and_delete(papi):
    media_id = _upload(papi)
    assert papi.get(f"/media/{media_id}").status_code == codes.OK
    assert papi.delete(f"/media/{media_id}").status_code == codes.NO_CONTENT


def test_foreign_download_forbidden(papi):
    media_id = _foreign_package()
    try:
        assert papi.get(f"/media/{media_id}").status_code == codes.FORBIDDEN
    finally:
        shutil.rmtree(opts.media_path / media_id)


def test_foreign_delete_forbidden(papi):
    media_id = _foreign_package()
    try:
        assert papi.delete(f"/media/{media_id}").status_code == codes.FORBIDDEN
    finally:
        shutil.rmtree(opts.media_path / media_id)


def test_foreign_embed_forbidden(papi):
    media_id = _foreign_package()
    try:
        response = papi.post(f"/metadata/{media_id}", json={"name": "x"})
        assert response.status_code == codes.FORBIDDEN
    finally:
        shutil.rmtree(opts.media_path / media_id)


def test_owner_embed_missing_file(papi):
    """The owner passes the privacy check but the media file has vanished."""
    media_id = _upload(papi)
    (opts.media_path / media_id / "test-image.jpg").unlink()
    try:
        response = papi.post(f"/metadata/{media_id}", json={"name": "x"})
        assert response.status_code == codes.NOT_FOUND
    finally:
        shutil.rmtree(opts.media_path / media_id)
