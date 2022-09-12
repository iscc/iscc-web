def test_tus_options(client_session):
    """
    An OPTIONS request MAY be used to gather information about the Server's current
    configuration. A successful response indicated by the 204 No Content or 200 OK
    status MUST contain the Tus-Version header. It MAY include the Tus-Extension
    and Tus-Max-Size headers.
    """

    response = client_session.options("/tus")
    assert response.status_code == 204
    expected = {
        "tus-resumable": "1.0.0",
        "tus-version": "1.0.0",
        "tus-max-size": "104857600",
        "tus-extension": "creation",
    }
    assert set(expected.items()).issubset(set(response.headers.items()))


def test_tus_head_not_found(client_session):
    """
    If the resource is not found, the Server SHOULD return either the 404 Not Found, 410 Gone or
    403 Forbidden status without the Upload-Offset header.

    The Server MUST prevent the client and/or proxies from caching the response by adding the
    Cache-Control: no-store header to the response.
    """
    response = client_session.head("/tus/noexist")
    assert response.status_code == 404
    assert response.headers.get("Cache-Control") == "no-store"


def test_tus_head(client_session):
    """
    The Server MUST always include the Upload-Offset header in the response for a HEAD request,
    even if the offset is 0, or the upload is already considered completed. If the size of the
    upload is known, the Server MUST include the Upload-Length header in the response.
    """
