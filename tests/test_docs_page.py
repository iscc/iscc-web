"""The API reference page at /docs: its local assets resolve and its external files are integrity-checked."""

import re
from pathlib import Path

import httpx

import iscc_web
from tests.conftest import server_host, server_port

BASE_URL = f"http://{server_host}:{server_port}"
PAGE = Path(iscc_web.__file__).parent / "static" / "docs" / "index.html"


def local_paths(html):
    # type: (str) -> set[str]
    """Site-absolute paths referenced by src/href attributes and CSS url() values in `html`."""
    attributes = re.findall(r'(?:src|href)="(/[^"#]*)"', html)
    css_urls = re.findall(r'url\("(/[^"]+)"\)', html)
    return set(attributes) | set(css_urls)


def test_docs_page_assets_are_served():
    page = httpx.get(f"{BASE_URL}/docs")
    assert page.status_code == 200
    paths = local_paths(page.text)
    assert "/static/images/iscc-generator-white-coral.svg" in paths
    assert "/static/images/iscc-logo-white-coral.svg" in paths
    assert "/static/fonts/readex-pro-latin-400-normal.woff2" in paths
    for path in sorted(paths):
        assert httpx.get(f"{BASE_URL}{path}").status_code == 200, path


def test_docs_page_external_files_carry_integrity():
    tags = re.findall(r"<(?:script|link)\b[^>]*https?://[^>]*>", PAGE.read_text(encoding="utf-8"), re.DOTALL)
    assert len(tags) == 2
    for tag in tags:
        assert re.search(r'integrity="sha384-[A-Za-z0-9+/=]{64}"', tag), tag
        assert 'crossorigin="anonymous"' in tag, tag
        assert re.search(r"@\d+\.\d+\.\d+/", tag), tag
