# -*- coding: utf-8 -*-
from httpx import codes
from iscc_samples import images
import base64


def test_create_iscc_location_and_result(api):
    content = images()[0].open("rb").read()
    headers = {
        "X-Upload-Filename": base64.b64encode("test-image.jpg".encode("utf-8")),
        "Content-Type": "image/jpeg",
    }
    response = api.post("/iscc", content=content, headers=headers)

    assert response.headers.get("Location").startswith("/api/v1/media/")

    result = response.json()
    del result["media_id"]
    del result["content"]
    assert result == {
        "$schema": "http://purl.org/iscc/schema/0.4.0.json",
        "@context": "http://purl.org/iscc/context/0.4.0.jsonld",
        "@type": "ImageObject",
        "datahash": "1e209db4c0d9e68c5203dc8c2fefe52fa5d54671be3a3253e06888cace7c60e5a743",
        "filename": "test-image.jpg",
        "filesize": 53256,
        "height": 133,
        "iscc": "ISCC:KECXNDSZVTTX2LDQYNBTBHR4T2HGOYBAGBNWZ767PKO3JQGZ42GFEAY",
        "mediatype": "image/jpeg",
        "metahash": "1e20304ab0c98a760be580dfa20716f2912d7ae30ec82b5f48b01dcf8f008d42568d",
        "mode": "image",
        "name": "test image",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }


def test_get_iscc_ok(api):
    response = api.get("/iscc/061knt35ejv6o")
    assert response.status_code == codes.OK
    assert response.json() == {
        "$schema": "http://purl.org/iscc/schema/0.4.0.json",
        "@context": "http://purl.org/iscc/context/0.4.0.jsonld",
        "@type": "ImageObject",
        "datahash": "1e20b46b2257d6c6248f0b2130affc644088cc07f31219394f28523e7742441e91fd",
        "filename": "test-image.jpg",
        "filesize": 8771,
        "height": 128,
        "iscc": "ISCC:KECXNDSZVTTX2LDQVXGTITPTHQYDJJZQLCUWSZT62C2GWISX23DCJDY",
        "mediatype": "image/jpeg",
        "metahash": "1e20304ab0c98a760be580dfa20716f2912d7ae30ec82b5f48b01dcf8f008d42568d",
        "mode": "image",
        "name": "test image",
        "thumbnail": "data:image/webp;base64,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",
        "width": 128,
    }


def test_get_iscc_not_found(api):
    response = api.get("/iscc/061ko3i97hshu")
    assert response.status_code == codes.NOT_FOUND
