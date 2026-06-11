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
        "$schema": "http://purl.org/iscc/schema/0.8.0.json",
        "@context": "http://purl.org/iscc/context/0.8.0.jsonld",
        "@type": "ImageObject",
        "datahash": "1e209db4c0d9e68c5203dc8c2fefe52fa5d54671be3a3253e06888cace7c60e5a743",
        "filename": "test-image.jpg",
        "filesize": 53256,
        "generator": "iscc-sdk - v0.9.3",
        "height": 133,
        "iscc": "ISCC:KECXNDSZVTTX2LDQYNBTBHR4T2HGOYBAGBNWZ767PKO3JQGZ42GFEAY",
        "mediatype": "image/jpeg",
        "metahash": "1e20304ab0c98a760be580dfa20716f2912d7ae30ec82b5f48b01dcf8f008d42568d",
        "mode": "image",
        "name": "test image",
        "thumbnail": "data:image/webp;base64,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",
        "units": [
            "ISCC:AADXNDSZVTTX2LDQWWLJUWUK3DGIQV27EFWEUI2AEXNONCRDWUSE2OY",
            "ISCC:EED4GQZQTY6J5DTHQ2DWCPDZHQOM6QZQTY6J5DTFZ2DWCPDZHQOMXDI",
            "ISCC:GADWAIBQLNWP7X32J3INMAMDUJ4QMN67BBQKVTVZIWHXQ7QJIKHYTBY",
            "ISCC:IADZ3NGA3HTIYUQD3SGC737FF6S5KRTRXY5DEU7ANCEMVTT4MDS2OQY",
        ],
        "width": 200,
    }


def test_create_iscc_unsupported_mediatype_fallback(api):
    """Unsupported media types yield a 2-unit wide ISCC-SUM (Data + Instance) by default."""
    content = b"binary gibberish that is no known mediatype"
    headers = {
        "X-Upload-Filename": base64.b64encode("data.bin".encode("utf-8")),
        "Content-Type": "application/octet-stream",
    }
    response = api.post("/iscc", content=content, headers=headers)
    assert response.status_code == codes.CREATED
    result = response.json()
    del result["media_id"]
    del result["content"]
    assert result == {
        "$schema": "http://purl.org/iscc/schema/0.8.0.json",
        "@context": "http://purl.org/iscc/context/0.8.0.jsonld",
        "@type": "CreativeWork",
        "datahash": "1e20e71d4ae9d38271d900dd98e8ca9ff1f42075038d2139f5aed93c8329da6e7b4e",
        "filename": "data.bin",
        "filesize": 43,
        "generator": "iscc-sdk - v0.9.3",
        "iscc": "ISCC:K4ANLI74MSJU22HRO6FI2IOR3IVCNZY5JLU5HATR3EAN3GHIZKP7D5A",
        "mediatype": "application/octet-stream",
        "units": [
            "ISCC:GAD5LI74MSJU22HRO6FI2IOR3IVCNZUI5AQQJLU3V6BCJDETHFQDYEI",
            "ISCC:IAD6OHKK5HJYE4OZADOZR2GKT7Y7IIDVAOGSCOPVV3MTZAZJ3JXHWTQ",
        ],
    }


def test_get_iscc_ok(api):
    response = api.get("/iscc/061knt35ejv6o")
    assert response.status_code == codes.OK
    assert response.json() == {
        "$schema": "http://purl.org/iscc/schema/0.8.0.json",
        "@context": "http://purl.org/iscc/context/0.8.0.jsonld",
        "@type": "ImageObject",
        "datahash": "1e20a8c645d48691e1e68af375a7a39346992353ae12b853befe499473fe9e19fcb6",
        "filename": "test-image.jpg",
        "filesize": 11246,
        "generator": "iscc-sdk - v0.9.3",
        "height": 128,
        "iscc": "ISCC:KECSIOC2VIDHWPNSVXGTITPTHQYDJJRQDGUSCJTQ2CUMMROUQ2I6DZQ",
        "mediatype": "image/jpeg",
        "metahash": "1e2026cd8567c2c4cc8b68c50229dccc94cbedd62f3dd25cd39e4a8b92d4b1814c1f",
        "mode": "image",
        "name": "Test Title",
        "thumbnail": "data:image/webp;base64,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",
        "width": 128,
    }


def test_get_iscc_not_found(api):
    response = api.get("/iscc/061ko3i97hshu")
    assert response.status_code == codes.NOT_FOUND
