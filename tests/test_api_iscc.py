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
    del result["generator"]
    assert result == {
        "$schema": "http://purl.org/iscc/schema/0.5.0.json",
        "@context": "http://purl.org/iscc/context/0.5.0.jsonld",
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
        "thumbnail": (
            "data:image/webp;base64,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"
        ),
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
        "thumbnail": (
            "data:image/webp;base64,UklGRsIJAABXRUJQVlA4ILYJAAAQMQCdASqAAIAAPrVQoUwnJKMipRM+WOAWiWMAyBhfrABL3kvNxvDOeZ3WyMZ6c/O9E2zd2n/bhPd3F/vHGyRYPc43XnR9gejbxmPuv+96JDUb9dF88fh5d3jSs7HjS6CMXLbtOgJGU23g8jlf35ZRJWieHMSOmuvP6D/XGcpQ5JhOm3SFamPgsBk1Hz/ego+cwQ0+cWH0yNZ4xRSMZ2TyTgEtjYs4REJzs7jwWUDGLmZbfwwnB/reU0Ao/RBThHGcXK3REwuWxnngPSK/IaVVYsjzJELQQUynkonM92Ua3I/ESEYUs31fhJnzGksVlMd4V32FXuiQEJWKWmy0B3amB9zDguMzpu0dmMp9h/yjnJWoV+c8YTlgs47joxkqTi20jzu+Wg6u+O5S2UM8JpetZLlGUCc19iTA2W74ItrVUqK0OZJWq9u2A4tgbmpShjR7pAapl4tlPwW/d4Ub/3LVlnlHdTCKgNggkP0B17oauy5YU43eJ06m5LCWNT521LCgaVzqO91SWAXZ36lg3VQ4IAD+8BEYM2UCmV+vbqUaB2zJG7dh/jxLVbp3OZ0r+bdH2Pqv5wnecelHgDHBpKTkizZB/3+AdeoDN+WBLGuS1JKmSeECOhfLkjPQ0AYJuYcn2CXgR8sBEBGeBEG+KmMtEn9lcPGteIquxzGdcyjuQ1a113kLfpENJKLM866Kp0ugdYa98RjymVLHuz5vpJclad85MfuGwfoaW/uuYmYTeHYa7P3AGWTkly5SlX3P1LDLZzTZf2bHGbbnktOZG3jALObmYVwM/kPOBTmD3T7TxMdd1OnLhXrgPbsMGEGEY1W2nyldK9t9z81f6Pf/I6wjCpYl90W8JeIcl8yy8Ivz0zUEmtSgTJoXVXvu6FM43G/b5lixp+yY+7LcEq4aOjyMOW+AMhUkMFr9A7bTgLLldSLhOg9kO6xtVHfLlA0XwW1xsUmrBNr3AM4i5RyHNSmgHDod/6i7F5SuOaEUanVn26j2f6HNYQtkWGTOT8ZVftQID5S1OGAuqazoad9yExeGA7nkaGFMinxvsVBnNhLkk3ygmcnT1GecR7eRTEnx/UCg1G04fXOqamFIZgzHUiXWERtzQkKFH2AkxlEoutLn9rbJqEvH/kQ+arqrRBWhfqZzW/QJYAsh4kUOUKjIWbGXqoYajuCSaa2jI6bNXGzVVrglsFuQdziYhlWOuyKyGYEEnpCPEjpY5aB9Q3D22sdcUVaW8J/tZ00djD6VV0NB2UkrE0OiMICoDGl0rzciq9vo95AYvDtl5n6AqWOsHI9syUW5DjpCj5DmIDjFoRF0zPAqo/md1QbsolER1D0VhGzwWCfF9dqedRmPmmpU3wo7kHcDWyAFajIHr368sEiJddxem4DMX+QKyU7fq7DW+zmv+zz5XcqnQ85qj4V6sgV3gxZYA8jWfBzPcOw3blFO8TxUoIcbQMEDDShSBGAAZVbsbftGnzX7u8+VaIHRgYksjQdVzWl6oYedqKY6phzIHSRvOocBWcjmOnidxL731qIRo2jPLX08a/wEkU0z7Zjln8rqOpwRedKSljpcJEtoDr51psqU+6O41vukmNyAxc9d0h5aVKCXGLPrCQcUty90OUYyZiMKUURg6E4CpPcyI+jSsEsFqHydwpGGrvlKJvSAnEk7yYc/PVJuoegj++SqYz0xRXSmZHwS0IJWtS8TDXs45fAMJa7ocZZ6DqoscmvJbj/FGvDiZxLFFVIGVsJcg/BE9mVD60Fron94T69r/5XqnxN56dPv8sL4Cs4/4tfN5sGUX8Rm/Pgj2KZWV4xeS2ISDtxnXCUlrtDaGJ/eYr92ua30zCdTTgU0vdEcQ+CdDSYzCtQiUHrQ9MaGPD0+R5uok4SbfDqSqlCmHu5FMEOOYoI10R5a5xbQNIsQ1EhM5ncyne72KNMjisVYH+M3hMS++rFpTu9VJFWiVwAFgRIfgn1nTIAl4jWhzxxIeBFY4NkY9nvNHUSmxhld2ny1uQ6AViDYS5xDpKFVnyTTIM6VITyWcFoSbcLO4P4rh9ZAUkj/T1scFdRAxYC6gn78eSjGHmo1tkEpbtEnYy5TBw6KCc7lHFBXyNCBihF0Rn5HSmgWoNixK4fU2Y6k/sf9uguC4knVCemz0My+rx5zFl0kxw11QmjRh3rMChwq9yHd/NsJmG0cNoDbWxeBBDi3wxg70x0A+rqNrAv01SrV9bmvon8ow3MAU8luHUQ7Nih602Zpuyx/MmO4nD1uQgzrIbRugzjt10EUHaGqkxohfg3vS30Y3G+IA3NV/LPAo7o3EcLDEhWM70zlO8ZxyOTw7c1iHjKTAhefLXE0tgFZ6qKVHtaDhqwhaNeie9Pxnq8ZzUpF5ZFCCWQ4ShJ38tGTcmJgXhVeUcDxlOpsZPPFRU0or3rpmXhKIxmTguztfKod5sb8xOWgydkRZsvXClRKZ3z6co2/OjNlMAVrvwq/4cXq7lwbN1kO8Iwwv8dQquaW7kQf2H1P8EhXWOdu/fZxtxGZFbl6xEBH0H4wv6JlupmgKQUDa5nOcjQ9HqdEPxUJjqrwun36cbCuzKBNbvH9NrV0LFsSNdpyiijBrx37HrmQdur1xsHOyytYVl0ZWuHtPPafBv5KC/dT2b5Smkj36W3CepiGtc8VjKXFf9NLoFqghBWt7TzHA/GeeC7KOp7yh2NMaNFfoLEtKHWsSmXUpfT3H1ZoMyxawWMW7i4WY3kEt6RXixKzbnizNzJhuHrNWg0NxjcJg+tJMPJ9v9zCnrkThMEOok5r8wHHRCUP9k2zaM1j9ESjkY8G5QvSzXB2U82IQQ5NhAXFH/R6IUhRu5HvQXZhmk98Ey5ZwIwRrSSoDTWvkFUVP3TzKsGvaXGUxVe80QKIJUjXP5R6kBmonoEQY/k1a/Qu6/omm5BNFUXnnnoncjrT76uZpMof21C9Gb9TwtVXLmAC4dOJT0f6vCXV8errKmvcbSbmEQ3utchgGi/Fa+DIqG7udf1XdzQnUjI3TxEk+xX4wxNgPh0ftgiLugeAMeaMckLf5to+ot6F/7oZDfPmyu7IJYx2jOB7F5RFRoqfhI8ZHLra9baCSRo0Cu2V99Dvt+1RgZtBRe3s7FMSJqVeLhwjSTOBIfoL0q3X9LSWhC5rz6InfP9ugN5MCP3+Q2s+2GcpUIoG07GC+6NPaXBIClINk/N2eHuhk5mnHWt5QVM28Cdmd7ck7RjbOR9fRM857RcUNpb+9nTNNW0x+rHxFGYfYJUhwyX+RFtEK+3DTGgpeA5nT2381pQIWaD/fYLdsUmYNZOgAPgApYAAAA=="
        ),
        "width": 128,
    }


def test_get_iscc_not_found(api):
    response = api.get("/iscc/061ko3i97hshu")
    assert response.status_code == codes.NOT_FOUND
