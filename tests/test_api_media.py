# -*- coding: utf-8 -*-
import base64
from httpx import codes
from iscc_samples import images


def test_upload_and_delete_file(api):
    # upload
    content = images()[0].open("rb").read()
    headers = {
        "X-Upload-Filename": base64.b64encode("test-image.jpg".encode("utf-8")),
        "Content-Type": "image/jpeg",
    }
    response = api.post("/media", content=content, headers=headers)

    assert response.status_code == codes.CREATED

    body = response.json()
    assert "/api/v1/media/" in body["content"]

    # check location header
    media_id = response.json()["media_id"]
    assert media_id in response.headers.get("location")

    # download
    response = api.get(f"/media/{media_id}")
    assert response.status_code == codes.OK

    # delete
    response = api.delete(f"/media/{media_id}")
    assert response.status_code == codes.NO_CONTENT


def test_download_missing(api):
    response = api.get(f"/media/161knt35ej404")
    assert response.status_code == codes.NOT_FOUND
