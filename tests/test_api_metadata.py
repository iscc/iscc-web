# -*- coding: utf-8 -*-
from httpx import codes


def test_extract(api):
    response = api.get("/metadata/061knt35ejv6o")
    assert response.status_code == codes.OK
    assert response.json() == {"name": "Test Title"}
