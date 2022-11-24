# -*- coding: utf-8 -*-
from httpx import codes
from iscc_samples import images
import base64


def test_upload_extract_embed_download(api):
    # upload
    content = images("png")[0].open("rb").read()
    headers = {
        "X-Upload-Filename": base64.b64encode("test-image.jpg".encode("utf-8")),
        "Content-Type": "image/jpeg",
    }
    response = api.post("/media", content=content, headers=headers)
    media_id = response.json()["media_id"]

    # extract
    response = api.get(f"/metadata/{media_id}")
    assert response.status_code == codes.OK
    assert response.json() == {"creator": "Another Cat Lover", "name": "Concentrated Cat PNG"}

    # embed
    metadata = {
        "name": "The Never Ending Story",
        "description": "a 1984 fantasy film co-written and directed by *Wolfgang Petersen*",
        "meta": "data:application/json;charset=utf-8;base64,eyJleHRlbmRlZCI6Im1ldGFkYXRhIn0=",
        "creator": "Joanne K. Rowling",
        "license": "https://example.com/license-terms-for-this-item",
        "acquire": "https://example.com/buy-license-for-item-here",
        "credit": "Frank Farian - Getty Images",
        "rights": "Copyright 2022 ISCC Foundation - www.iscc.codes",
    }

    response = api.post(f"/metadata/{media_id}", json=metadata)
    assert response.status_code == codes.CREATED
    result = response.json()
    media_id = result["media_id"]
    assert result == {
        "$schema": "http://purl.org/iscc/schema/0.4.0.json",
        "@context": "http://purl.org/iscc/context/0.4.0.jsonld",
        "@type": "ImageObject",
        "acquire": "https://example.com/buy-license-for-item-here",
        "content": f"http://localhost:44555/api/v1/media/{media_id}",
        "creator": "Another Cat Lover, Joanne K. Rowling",
        "datahash": "1e201d022472b35f48c92ea376c620a6303901751a3839cce573178cb576968c3a4d",
        "description": "a 1984 fantasy film co-written and directed by *Wolfgang Petersen*",
        "filename": "test-image.jpg",
        "filesize": 57540,
        "height": 133,
        "iscc": "ISCC:KECTN76LTY522ZPCYNBTBHR4T2HGO6RDNMLX4HWUMQOQEJDSWNPURSI",
        "license": "https://example.com/license-terms-for-this-item",
        "media_id": media_id,
        "mediatype": "image/jpeg",
        "meta": "data:application/json;charset=utf-8;base64,eyJleHRlbmRlZCI6Im1ldGFkYXRhIn0=",
        "metahash": "1e20c9de45e7067944d16802651b639f31245968a2cfd59a01f351fee07e19116069",
        "mode": "image",
        "name": "The Never Ending Story",
        "rights": "Copyright 2022 ISCC Foundation - www.iscc.codes",
        "thumbnail": "data:image/webp;base64,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",
        "width": 200,
    }

    # download
    response = api.get(f"/media/{media_id}")
    assert response.status_code == codes.OK
