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
        # "acquire": "https://example.com/buy-license-for-item-here", # TODO Review
        "credit": "Frank Farian - Getty Images",
        "rights": "Copyright 2022 ISCC Foundation - www.iscc.codes",
    }

    response = api.post(f"/metadata/{media_id}", json=metadata)
    assert response.status_code == codes.CREATED
    result = response.json()
    media_id = result["media_id"]
    del result["generator"]
    assert result == {
        "$schema": "http://purl.org/iscc/schema",
        "@context": "http://purl.org/iscc/context",
        "@type": "ImageObject",
        "content": f"http://localhost:44555/api/v1/media/{media_id}",
        "creator": "Another Cat Lover, Joanne K. Rowling",  # TODO review
        "datahash": "1e20f7c91255323e07c4f95c159a2623526f68b4a629c29aa1a0eadb95286a1116e5",
        "description": "a 1984 fantasy film co-written and directed by *Wolfgang Petersen*",
        "filename": "test-image.jpg",
        "filesize": 57334,
        "height": 133,
        "iscc": "ISCC:KECTN76LTY522ZPCYNBTBHR4T2HGO6RDNMZX4P6UMT34SESVGI7APRA",
        "license": "https://example.com/license-terms-for-this-item",
        "media_id": media_id,
        "mediatype": "image/jpeg",
        "meta": "data:application/json;charset=utf-8;base64,eyJleHRlbmRlZCI6Im1ldGFkYXRhIn0=",
        "metahash": "1e20c9de45e7067944d16802651b639f31245968a2cfd59a01f351fee07e19116069",
        "mode": "image",
        "name": "The Never Ending Story",
        "rights": "Copyright 2022 ISCC Foundation - www.iscc.codes",
        "thumbnail": "data:image/webp;base64,UklGRsYFAABXRUJQVlA4ILoFAABwIgCdASqAAFUAPxFyr1KsJiQnrhkqYYAiCWcA0NO4SzE4K729xs0KGE3TPf58LAwDWfcLC3d0xi8kjSpMSal8MME9Dkc7+SfOysASz0517nKQJQhJnjLjM10EuxQsO338neNVD0h5ihTyOGuaMBa/aF0wgoQq+uBaGlVXrTlFOF08iTVVbRj+9f60o2MbQWOKnWpQfydPftRmdXgnBdZu/z/lqnnGCHlDJNr1t80zujPSolLYAodnFkiUYGrQMuMGCtJz5/D4JUvMF7mZ2vowhrj3N6BwAuxgfcX97HkmQIeYl3C3eg7dOoufvW24Am/i/iMmS6XnCMW3gbiN9S/4dTYJ/ZPa/dXE2Gz9dIFkEa/tYyQ418LhlQwh3AD+9xtO0Qfk17nyoJMFdziQFPZz1KYYlpfULSDIgbTRRDlGGBMi6k6nsi7OsQ0j1rnQhfua79tMCfO3jFeMoB4REOpkALW6V2ZpUYblhFqY/ZzM5twYPP1hNi33QUFwQP+oAFPSyfU4lV2YFN0Be5mqSvPsDrUBhI7XWr6R0xU9GEVSGqhPBEs69ysg2BaigCpHFOcqw+VrLtsISCI39BX55LdkTGcjnf6/QTBxHXtJ2M6duEKYl3sRWiMh4w1ma2JPqowcUuttr6czP4xMR4C39UViot0K+L9Fqzm+P8u4ezUqjX0VyKiFb8WEHm7/m7vBz5bwjE/F3t7AWzozfC2BWpggw6eCNloMT3+Qkf1wPMTg3REesutDjJG9vOc8Eu0pJgmIr4GJJNeiDCkJzZ/MZKO1XW7smwZiCK9Rp11+Nm8og35M02IXMdR/baDex1KB1zDCFCAPnPWtkzhr0pEDZ8EOb47Bh6sk7IGVWxjHpgRhSyEp+WacIMw00FNVhp7xvKgTcvCSBX2rTxmQv5K8Uku2Jk+Jp4AiQ2+NVWb311HTfifFcxOtKluSEZ3n4/WCFe+fvtCVjTzfR6fUlrUmFXQrDWLWXTep+ohjKhFL7vZKiMezMygeqfn2uztDMaI0xTDM2UrOCBNLBso/tMxB63aa3QsM+sfAl7gJfT16L62WgxNHf3QyYBaA465pYSNx5p5K72bosKtt1DZMJlrHczWNbrt+5nerLrTxcWVvU4IZ4ioezwuOgiakg7JkPZ72OMcoomVYiy6WgLLlfx4Sd786L+ppyAkpXOw1EDi8CTPhNwLoDhKtcgAMsuxrFZ46kMoZ5G7Pd8axW+/RR0IGDbHPSj9bjAK3SCxKMG/NVcApdR2atgYR49K+D7mZtTriKTlLR258TynrkZlYtJgyKFCF9TofxOCMD9x74az6M2Ohof2aXwKYtSkoISostsbddNgDvbhl6LM9GNHUoF2yxjGBzzI0BppJ6ZINh+oYSPLhepzoTqK+3Dayyk6vCRv56twMXTkZ5MOk9NPTGrpbnLjR9MpbeEqQrYP9UL8qbyIU9oduNJfQjdT1gz9ciSKSqXErzVqxJNrKIZzSyhbgzjJ/tgUntGTpiXJE5+xAGiiDTG4jQiZ7aTYzYCoxuRTt8qB2X7ZjyJdnLjtD+1TckrSKmtkjdEjNIams8jZgxJq0u16TQHS3lbrOTfLkKYD8JApK/d6rrl4i99Nxg71s4LAmIlVA26V1lBcUADlZHalf8dMiu1AkBH0+vzweOGSuWDXyasCCA1Hb1iNadLefcG5dyuGlawoGIdlOWz1fgiAbuF0i15lv0TFMzvJo6eL8A1FgnGJS9F4F25aRZ32Q7ACUfDif7bN4aUdUlpRsUIom4LjAbGSDrhYfVCPE4C+f0aaXtvjyJwdQgPPyoXKrkApy5+rzsfW3iOR/A0tu4/dG9Sug5QHOgS8MccWkaxtAIGSDUWOhkTTPHMZn/zyJH8HkpMALTdSsEQJW5j8kfh7pAeHoQJOp4TrazFJ1aJo1iReTFUge0uNHQnuZmFPYF7rAdFUkF0FNogAAAA==",
        "width": 200,
    }

    # download
    response = api.get(f"/media/{media_id}")
    assert response.status_code == codes.OK
