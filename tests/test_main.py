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
        "tus-max-size": "1073741824",
        "tus-extension": "creation,termination",
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


def test_tus_post_length_missing(client_session):
    """
    The Client MUST send a POST request against a known upload creation URL to request a new upload
    resource. The request MUST include one of the following headers:
        a) Upload-Length to indicate the size of an entire upload in bytes.
        b) Upload-Defer-Length: 1 if upload size is not known at the time. If the
        Upload-Defer-Length header contains any other value than 1 the server should return a
        400 Bad Request status.
    """
    response = client_session.post("/tus", headers={"Tus-Resumable": "1.0.0"})
    assert response.status_code == 400


def test_tus_post_length_to_big(client_session):
    """
    If the length of the upload exceeds the maximum, which MAY be specified using the Tus-Max-Size
    header, the Server MUST respond with the 413 Request Entity Too Large status.
    """
    response = client_session.post(
        "/tus",
        headers={
            "Tus-Resumable": "1.0.0",
            "Upload-Metadata": "filename d29ybGRfZG9taW5hdGlvbl9wbGFuLnBkZg==,is_confidential",
            "Upload-Length": "1073741825",
        },
    )
    assert response.status_code == 413


def test_tus_post(client_session):
    response = client_session.post(
        "/tus",
        headers={
            "Content-Length": "0",
            "Upload-Length": "100",
            "Tus-Resumable": "1.0.0",
            "Upload-Metadata": "filename d29ybGRfZG9taW5hdGlvbl9wbGFuLnBkZg==,is_confidential",
        },
    )
    assert response.status_code == 201
    assert "Location" in response.headers
