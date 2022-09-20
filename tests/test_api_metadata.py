# -*- coding: utf-8 -*-
from httpx import codes


def test_extract(api):
    response = api.get("/metadata/061knt35ejv6o")
    assert response.status_code == codes.OK
    assert response.json() == {"name": "Test Title"}


def test_embed(api):
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
    response = api.post(f"/metadata/061knt35ejv6o", json=metadata)
    assert response.status_code == codes.CREATED
    result = response.json()
    media_id = result["media_id"]
    assert result == {
        "$schema": "http://purl.org/iscc/schema/0.3.9.json",
        "@context": "http://purl.org/iscc/context/0.3.9.jsonld",
        "@type": "ImageObject",
        "iscc": "ISCC:KECTN76LTY522ZPCVXGTITPTHQYDJNTSDGUSWJDU2DKOCDA6LSJ44GY",
        "name": "The Never Ending Story",
        "description": "a 1984 fantasy film co-written and directed by *Wolfgang Petersen*",
        "meta": "data:application/json;charset=utf-8;base64,eyJleHRlbmRlZCI6Im1ldGFkYXRhIn0=",
        "acquire": "https://example.com/buy-license-for-item-here",
        "content": f"http://localhost:44555/api/v1/media/{media_id}",
        "creator": "Joanne K. Rowling",
        "datahash": "1e20d4e10c1e5c93ce1b8c1ed03018c2f9f3a836d7441ae41317eff37d2349e5c0e4",
        "filename": "test-image.jpg",
        "filesize": 12012,
        "height": 128,
        "license": "https://example.com/license-terms-for-this-item",
        "media_id": media_id,
        "mediatype": "image/jpeg",
        "metahash": "1e20c9de45e7067944d16802651b639f31245968a2cfd59a01f351fee07e19116069",
        "mode": "image",
        "rights": "Copyright 2022 ISCC Foundation - www.iscc.codes",
        "thumbnail": "data:image/webp;base64,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",
        "width": 128,
    }
