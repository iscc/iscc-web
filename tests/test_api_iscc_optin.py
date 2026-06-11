# -*- coding: utf-8 -*-
"""
Tests for the `semantic` and `granular` switches on POST /iscc.

`semantic` folds an experimental Semantic-Code ISCC-UNIT into the composite ISCC-CODE for text
and image content (5 units instead of 4 - the result is not a standard ISO 24138 identifier).
`granular` adds simprint features. Service defaults: semantic off, granular on (ISCC_SDK_* env
variables); explicit query params override per request.
"""

import base64
from httpx import codes
from iscc_samples import images, texts


# demo.jpg / demo.doc derive their Meta-Code from embedded metadata, so the expected values do
# not depend on the upload filename.
IMAGE = images("jpg")[0]
TEXT = texts("doc")[0]

IMAGE_ISCC = "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI"
IMAGE_UNITS = [
    "ISCC:AADWRY3VY6R5SNV4NUAGFYLVSJ3I7KX37VO6PYLC22DFONVH2GVZIPY",
    "ISCC:EED4GQZQTY6J5DTHQ2DWCPDZHQOM6QZQTY6J5DTFZ2DWCPDZHQOMXDI",
    "ISCC:GAD6Z2VJLX46FD6QVSSCW3BOUAIV5GRINTAHISA6UQIHPLWH3YBGAHQ",
    "ISCC:IADVKUU37LS33M6VGDCS6RGRHTGWU7DRB5RWEDOC3MOEHRKZFLRNZFY",
]

IMAGE_ISCC_SEMANTIC = "ISCC:KEDWRY3VY6R5SNV4BRNG6VVB7TGVZQ2DGCPDZHUOM7WOVKK57HRI7UCVKKN7VZN5WPKQ"
IMAGE_UNITS_SEMANTIC = [
    "ISCC:AADWRY3VY6R5SNV4NUAGFYLVSJ3I7KX37VO6PYLC22DFONVH2GVZIPY",
    "ISCC:CEDQYWTPK2Q7ZTK47HPOYUUTO3TCAZ6KNVUZODFMMY42S6O7RDCWFEA",
    "ISCC:EED4GQZQTY6J5DTHQ2DWCPDZHQOM6QZQTY6J5DTFZ2DWCPDZHQOMXDI",
    "ISCC:GAD6Z2VJLX46FD6QVSSCW3BOUAIV5GRINTAHISA6UQIHPLWH3YBGAHQ",
    "ISCC:IADVKUU37LS33M6VGDCS6RGRHTGWU7DRB5RWEDOC3MOEHRKZFLRNZFY",
]

TEXT_ISCC = "ISCC:KACV5NAQXBCHCWFWAYCJRAL5Z36G7AZALCN3HBKABNDND26WJ5IVG4I"
TEXT_UNITS = [
    "ISCC:AADV5NAQXBCHCWFWDAKH73TRQFFMMEC426IIPINQ3TY5ZKQRAJF7CDY",
    "ISCC:EADQMBEYQF6457DPBR6T57675QKCHTATASH4TQG5BJAIB6RDQHWNP6A",
    "ISCC:GADYGICYTOZYKQAL2YOJ27EBBQU5RZOAOKFVTTMZELKYE2WRJDPYB7Q",
    "ISCC:IADUNUPL2ZHVCU3RZCGR35N4BVBYSOY7UHSYMVFSYQSE4SI5AYAHUYI",
]

TEXT_ISCC_SEMANTIC = "ISCC:KADV5NAQXBCHCWFW7PXEY76RBZT52BQETCAX3TX4N6BSAWE3WOCUAC2G2HV5MT2RKNYQ"
TEXT_UNITS_SEMANTIC = [
    "ISCC:AADV5NAQXBCHCWFWDAKH73TRQFFMMEC426IIPINQ3TY5ZKQRAJF7CDY",
    "ISCC:CAD7X3SMP7IQ4Z65GJAIBDRXMWGZVIMG33FEYTEPLWGU4FS2KCG5DRQ",
    "ISCC:EADQMBEYQF6457DPBR6T57675QKCHTATASH4TQG5BJAIB6RDQHWNP6A",
    "ISCC:GADYGICYTOZYKQAL2YOJ27EBBQU5RZOAOKFVTTMZELKYE2WRJDPYB7Q",
    "ISCC:IADUNUPL2ZHVCU3RZCGR35N4BVBYSOY7UHSYMVFSYQSE4SI5AYAHUYI",
]

# Offsets and sizes are UTF-8 byte based (ISCC_SCT_BYTE_OFFSETS / ISCC_SDK_BYTE_OFFSETS
# defaults); for this pure-ASCII sample text they coincide with character offsets.
TEXT_SEMANTIC_FEATURES = {
    "maintype": "semantic",
    "subtype": "text",
    "version": 0,
    "byte_offsets": True,
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
    "offsets": [
        0,
        19,
        315,
        611,
        907,
        1325,
        1726,
        2262,
        2558,
        2994,
        3133,
        3401,
        3697,
        3964,
        4260,
        4556,
        4852,
        5270,
        5671,
    ],
    "sizes": [19, 452, 452, 298, 420, 403, 536, 436, 436, 139, 424, 452, 267, 452, 452, 298, 420, 403, 397],
}

TEXT_CONTENT_FEATURES = {
    "maintype": "content",
    "subtype": "text",
    "version": 0,
    "byte_offsets": True,
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


def test_create_iscc_explicit_false_params(api):
    result = upload(api, IMAGE, "demo.jpg", "?semantic=false&granular=false").json()
    assert result["iscc"] == IMAGE_ISCC
    assert result["units"] == IMAGE_UNITS  # units are listed by default (ISCC_SDK_ADD_UNITS)
    assert "features" not in result


def test_create_iscc_default_semantic_off_granular_on(api):
    default = upload(api, IMAGE, "demo.jpg").json()
    explicit = upload(api, IMAGE, "demo.jpg", "?semantic=false&granular=true").json()
    for volatile in ("media_id", "content"):
        del default[volatile]
        del explicit[volatile]
    assert explicit == default
    assert default["iscc"] == IMAGE_ISCC
    assert default["units"] == IMAGE_UNITS


def test_create_iscc_semantic_image(api):
    response = upload(api, IMAGE, "demo.jpg", "?semantic=true&granular=false")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == IMAGE_ISCC_SEMANTIC  # 5-unit composite including Semantic-Code
    assert result["units"] == IMAGE_UNITS_SEMANTIC
    assert "features" not in result


def test_create_iscc_granular_image_has_no_features(api):
    # The SDK has no granular image algorithm - the response must match a default request.
    default = upload(api, IMAGE, "demo.jpg").json()
    granular = upload(api, IMAGE, "demo.jpg", "?granular=true").json()
    for volatile in ("media_id", "content"):
        del default[volatile]
        del granular[volatile]
    assert granular == default


def test_create_iscc_semantic_granular_image_has_no_features(api):
    # Semantic simprints exist for text only - a granular semantic image request stays lean.
    response = upload(api, IMAGE, "demo.jpg", "?semantic=true&granular=true")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == IMAGE_ISCC_SEMANTIC
    assert result["units"] == IMAGE_UNITS_SEMANTIC
    assert "features" not in result


def test_create_iscc_semantic_text(api):
    response = upload(api, TEXT, "demo.doc", "?semantic=true&granular=false")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == TEXT_ISCC_SEMANTIC  # 5-unit composite including Semantic-Code
    assert result["units"] == TEXT_UNITS_SEMANTIC
    assert "features" not in result


def test_create_iscc_granular_text(api):
    response = upload(api, TEXT, "demo.doc", "?semantic=false&granular=true")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == TEXT_ISCC
    assert result["units"] == TEXT_UNITS
    assert result["features"] == [TEXT_CONTENT_FEATURES]


def test_create_iscc_semantic_granular_text(api):
    response = upload(api, TEXT, "demo.doc", "?semantic=true&granular=true")
    assert response.status_code == codes.CREATED
    result = response.json()
    assert result["iscc"] == TEXT_ISCC_SEMANTIC
    assert result["units"] == TEXT_UNITS_SEMANTIC
    assert result["features"] == [TEXT_SEMANTIC_FEATURES, TEXT_CONTENT_FEATURES]


def test_create_iscc_semantic_composite_decomposes(api):
    # The experimental 5-unit composite is a valid input for the explain endpoint.
    result = upload(api, TEXT, "demo.doc", "?semantic=true&granular=false").json()
    response = api.get(f"/explain/{result['iscc']}")
    assert response.status_code == codes.OK
    units = [unit["iscc_unit"] for unit in response.json()["units"]]
    assert units == [
        "ISCC:AAAV5NAQXBCHCWFW",
        "ISCC:CAA7X3SMP7IQ4Z65",
        "ISCC:EAAQMBEYQF6457DP",
        "ISCC:GAAYGICYTOZYKQAL",
        "ISCC:IAAUNUPL2ZHVCU3R",
    ]


def test_create_iscc_invalid_param_value(api):
    response = upload(api, IMAGE, "demo.jpg", "?semantic=banana")
    assert response.status_code == codes.BAD_REQUEST
