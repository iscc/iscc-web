# -*- coding: utf-8 -*-
"""Tests for opt-in semantic ISCC-UNITs and granular features on POST /iscc."""

import base64
from httpx import codes
from iscc_samples import images, texts


# demo.jpg / demo.doc derive their Meta-Code from embedded metadata, so the expected values do
# not depend on the upload filename.
IMAGE = images("jpg")[0]
TEXT = texts("doc")[0]

IMAGE_ISCC = "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI"
IMAGE_UNITS = [
    "ISCC:AAAWRY3VY6R5SNV4",
    "ISCC:CEAQYWTPK2Q7ZTK4",
    "ISCC:EEA4GQZQTY6J5DTH",
    "ISCC:GAA6Z2VJLX46FD6Q",
    "ISCC:IAAVKUU37LS33M6V",
]

TEXT_ISCC = "ISCC:KACV5NAQXBCHCWFWAYCJRAL5Z36G7AZALCN3HBKABNDND26WJ5IVG4I"
TEXT_UNITS = [
    "ISCC:AAAV5NAQXBCHCWFW",
    "ISCC:CAA7X3SMP7IQ4Z65",
    "ISCC:EAAQMBEYQF6457DP",
    "ISCC:GAAYGICYTOZYKQAL",
    "ISCC:IAAUNUPL2ZHVCU3R",
]

TEXT_SEMANTIC_FEATURES = {
    "maintype": "semantic",
    "subtype": "text",
    "version": 0,
    "simprints": [
        "XUj8aOg4CGm5Uosm-Ggxi7d9G9pa4NBMyBDDAhrkf00",
        "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
        "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
        "865-e3EKZ90ywBCONeXNmqGChMpMTI9dDU4eWlCL0dY",
        "--9K9-EeZ912CICDN3QLmrGG3s5NTIVdjy4fSliNk-I",
        "4-5I70E8Z90yNoiDlzULmmDG3s4NXodVjy4WWliMk0I",
        "8-9K_9E8Z91zaICCl3ULmzTG3u4MXoddjw4WWkGMkcY",
        "86pvUlEOZ90ywIDqH-WNiuGCxspNTI9cjU4WWlCP0VY",
        "c6p_VlEOZ90ywIDqH-SNiuGCxspNTI9cjU4WWlCP0VY",
        "82dsL9FKZ9wyyDGGlS2NuiGGhGpcbg9ZTU4eWkmN1dI",
        "-6pe_9EKZ90y4JCOFeWNmqGCxMpNTItdDU4eWlCP0dY",
        "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
        "865-e3EKZ90yYBCOP-XNmqGChMpMTI9cDU4eWlGL0dY",
        "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
        "--5Of_EKZ90ywJCOFeXNmqGGhMpMTI9djU4WWlGN0dY",
        "865-e3EKZ90ywBCONeXNmqGChMpMTI9dDU4eWlCL0dY",
        "--9K9-EeZ912CICDN3QLmrGG3s5NTIVdjy4fSliNk-I",
        "4-5I70E8Z90yNoiDlzULmmDG3s4NXodVjy4WWliMk0I",
        "8-9K_9E8Z91z4IGClH0LmjTG3u4MXoddjw4WWkGMkcY",
    ],
}

TEXT_CONTENT_FEATURES = {
    "maintype": "content",
    "subtype": "text",
    "version": 0,
    "byte_offsets": False,
    "simprints": [
        "k5TpwXVE3j9N5IBxm36c4hkXP6fHOv8bkY2f68_8XSg",
        "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
        "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
        "lp6NgXnE_C1c6ij12-w04RwZN4XJyP0KgIrbKYX81yo",
        "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
        "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
        "JfC6tnH1BuHFMviS2deReiUuelIIMvWWOozU6afjErU",
    ],
    "offsets": [0, 996, 1453, 2122, 4941, 5398, 6067],
    "sizes": [996, 457, 669, 2819, 457, 669, 1],
}


def upload(api, file_path, file_name, params=""):
    headers = {"X-Upload-Filename": base64.b64encode(file_name.encode("utf-8"))}
    return api.post(f"/iscc{params}", content=file_path.open("rb").read(), headers=headers)


def test_create_iscc_explicit_false_params_match_default(api):
    default = upload(api, IMAGE, "demo.jpg").json()
    explicit = upload(api, IMAGE, "demo.jpg", "?semantic=false&granular=false").json()
    for volatile in ("media_id", "content"):
        del default[volatile]
        del explicit[volatile]
    assert explicit == default
    assert "units" not in default
    assert "features" not in default


def test_create_iscc_semantic_image(api):
    response = upload(api, IMAGE, "demo.jpg", "?semantic=true")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == IMAGE_ISCC  # composite ISCC-CODE unchanged by opt-in
    assert result["units"] == IMAGE_UNITS
    assert "features" not in result


def test_create_iscc_granular_image_has_no_features(api):
    # The SDK has no granular image algorithm - the response must match a default request.
    default = upload(api, IMAGE, "demo.jpg").json()
    granular = upload(api, IMAGE, "demo.jpg", "?granular=true").json()
    for volatile in ("media_id", "content"):
        del default[volatile]
        del granular[volatile]
    assert granular == default


def test_create_iscc_semantic_text(api):
    response = upload(api, TEXT, "demo.doc", "?semantic=true")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == TEXT_ISCC  # composite ISCC-CODE unchanged by opt-in
    assert result["units"] == TEXT_UNITS
    assert "features" not in result


def test_create_iscc_granular_text(api):
    response = upload(api, TEXT, "demo.doc", "?granular=true")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == TEXT_ISCC
    assert "units" not in result
    assert result["features"] == [TEXT_CONTENT_FEATURES]


def test_create_iscc_semantic_granular_text(api):
    response = upload(api, TEXT, "demo.doc", "?semantic=true&granular=true")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == TEXT_ISCC
    assert result["units"] == TEXT_UNITS
    assert result["features"] == [TEXT_SEMANTIC_FEATURES, TEXT_CONTENT_FEATURES]


def test_create_iscc_invalid_param_value(api):
    response = upload(api, IMAGE, "demo.jpg", "?semantic=banana")
    assert response.status_code == codes.BAD_REQUEST
