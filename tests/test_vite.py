"""Tests for the Vite Jinja2 integration tags (dev and production modes)."""

import json

import pytest
from jinja2 import Environment

from iscc_web import vite


MANIFEST = {
    "frontend/main.ts": {
        "file": "assets/main.123.js",
        "css": ["assets/main.123.css"],
        "imports": ["_shared.456.js", "_nocss.789.js"],
    },
    "_shared.456.js": {"file": "assets/shared.456.js", "css": ["assets/main.123.css"]},
    "_nocss.789.js": {"file": "assets/nocss.789.js"},
}


@pytest.fixture
def env():
    environment = Environment()
    vite.register_extensions(environment)
    return environment


@pytest.fixture
def prod(monkeypatch):
    monkeypatch.setattr(vite, "VITE_DEV_MODE", False)
    monkeypatch.setattr(vite, "VITE_MANIFEST", MANIFEST)


def render(env, source):
    return env.from_string(source).render()


def test_dev_mode_hmr_client(env):
    out = render(env, "{% vite_hmr_client %}")
    assert out == '<script type="module" crossorigin="" src="http://localhost:5173/@vite/client"></script>'


def test_dev_mode_asset(env):
    out = render(env, "{% vite_asset 'frontend/main.ts' %}")
    assert out == '<script type="module" crossorigin="" src="http://localhost:5173/frontend/main.ts"></script>'


def test_prod_mode_hmr_client_is_empty(env, prod):
    assert render(env, "{% vite_hmr_client %}") == ""


def test_prod_mode_asset_renders_css_and_script(env, prod):
    out = render(env, "{% vite_asset 'frontend/main.ts' %}")
    # CSS from the imported chunk comes first and is deduplicated against the entry's own CSS.
    assert out == (
        '<link rel="stylesheet" href="/static/dist/assets/main.123.css" />\n'
        '<script type="module" crossorigin="" src="/static/dist/assets/main.123.js"></script>'
    )


def test_prod_mode_missing_asset_raises(env, prod):
    with pytest.raises(RuntimeError, match="Cannot find missing.ts"):
        render(env, "{% vite_asset 'missing.ts' %}")


def test_prod_mode_without_manifest_raises(env, monkeypatch):
    monkeypatch.setattr(vite, "VITE_DEV_MODE", False)
    monkeypatch.setattr(vite, "VITE_MANIFEST", None)
    with pytest.raises(RuntimeError, match="Cannot find frontend/main.ts"):
        render(env, "{% vite_asset 'frontend/main.ts' %}")


def test_prod_mode_missing_import_raises(env, monkeypatch):
    monkeypatch.setattr(vite, "VITE_DEV_MODE", False)
    monkeypatch.setattr(vite, "VITE_MANIFEST", {"main.ts": {"file": "a.js", "imports": ["gone.js"]}})
    with pytest.raises(RuntimeError, match="Cannot find gone.js"):
        render(env, "{% vite_asset 'main.ts' %}")


def test_load_manifest(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"a": 1}))
    assert vite.load_manifest(path) == {"a": 1}


def test_load_manifest_missing_raises(tmp_path):
    with pytest.raises(RuntimeError, match="Could not find Vite manifest.json"):
        vite.load_manifest(tmp_path / "manifest.json")
