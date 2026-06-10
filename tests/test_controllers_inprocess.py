"""In-process tests for controller and worker paths that cannot be triggered over HTTP."""

import asyncio
import types
from concurrent.futures import Future

from iscc_samples import images

import iscc_web.api.mixins as mixins
import iscc_web.api.simprint as simprint_module
from iscc_web.api.iscc import Iscc
from iscc_web.api.media import Media
from iscc_web.api.metadata import Metadata
from iscc_web.api.mixins import FileHandler
from iscc_web.api.models import UploadMeta
from iscc_web.api.pool import Pool
from iscc_web.api.schema import InlineMetadata, SimprintRequest
from iscc_web.api.simprint import Simprint
from iscc_web.options import opts


class FakePool:
    """Executor stub returning canned results (or raising canned exceptions) per submit call."""

    def __init__(self, *results):
        self._results = list(results)

    def submit(self, fn, *args, **kwargs):
        future = Future()
        result = self._results.pop(0)
        if isinstance(result, Exception):
            future.set_exception(result)
        else:
            future.set_result(result)
        return future


def _fake_app(pool):
    """Stand-in for iscc_web.main.app exposing only the Pool service used by process_iscc."""
    return types.SimpleNamespace(services=types.SimpleNamespace(provider={Pool: pool}))


def _make_package(media_path, file_name="file.jpg", with_file=True):
    media_id = FileHandler.new_media_id()
    package = media_path / media_id
    package.mkdir()
    meta = UploadMeta(media_id=media_id, file_name=file_name, content_type="image/jpeg", user="0" * 64)
    (package / f"{media_id}.meta.json").write_text(meta.model_dump_json())
    if with_file:
        (package / file_name).write_bytes(b"fake image data")
    return media_id


def test_process_iscc_error_result(monkeypatch, tmp_path):
    monkeypatch.setattr(mixins, "app", _fake_app(FakePool(ValueError("processing failed"))))
    response = asyncio.run(Iscc().process_iscc(tmp_path / "file.jpg"))
    assert response.status == 422


def test_process_iscc_none_result(monkeypatch, tmp_path):
    monkeypatch.setattr(mixins, "app", _fake_app(FakePool(None)))
    response = asyncio.run(Iscc().process_iscc(tmp_path / "file.jpg"))
    assert response.status == 422


def test_delete_file_package_vanished(monkeypatch, tmp_path):
    """Simulate a package directory deleted between metadata read and package removal."""
    monkeypatch.setattr(opts, "media_path", tmp_path)
    media_id = _make_package(tmp_path)

    async def raise_not_found(path):
        raise FileNotFoundError(path)

    monkeypatch.setattr(mixins, "rmtree", raise_not_found)
    response = asyncio.run(Media().delete_file(None, media_id))
    assert response.status == 404


def test_embed_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(opts, "media_path", tmp_path)
    media_id = _make_package(tmp_path)
    pool = FakePool(ValueError("embedding failed"))
    response = asyncio.run(Metadata().embed(None, media_id, InlineMetadata(name="x"), pool))
    assert response.status == 422


def test_embed_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(opts, "media_path", tmp_path)
    media_id = _make_package(tmp_path)
    pool = FakePool(None)
    response = asyncio.run(Metadata().embed(None, media_id, InlineMetadata(name="x"), pool))
    assert response.status == 422


def test_code_semantic_unsupported_mode_returns_none():
    assert mixins.code_semantic("unused-path", "audio", granular=False) is None


def test_code_iscc_semantic_without_semantic_code(monkeypatch):
    """Media without a Semantic-Code algorithm keeps its plain unit list when semantic=true."""
    monkeypatch.setattr(mixins, "code_semantic", lambda fp, mode, granular: None)
    result = mixins.code_iscc(images("jpg")[0].as_posix(), semantic=True)
    assert len(result.units) == 4
    assert not any(unit.startswith("ISCC:C") for unit in result.units)


def test_simprint_processing_error():
    pool = FakePool(ValueError("simprint processing failed"))
    response = asyncio.run(Simprint().create_simprint(SimprintRequest(text="some text"), pool))
    assert response.status == 422


def test_text_simprints_without_semantic_features(monkeypatch):
    """Defensive path ported from iscc-search: sct result without features yields no semantic key."""
    monkeypatch.setattr(simprint_module.sct, "gen_text_code_semantic", lambda *args, **kwargs: {"features": []})
    result = simprint_module.text_simprints("hello world")
    assert result == {"CONTENT_TEXT_V0": ["JQ25bg1KF6BhSJXnr_eE_uFCcDd_l36NicEiIgzpa-M"]}


def test_text_simprints_with_empty_semantic_simprints(monkeypatch):
    """Defensive path ported from iscc-search: feature set without simprints yields no semantic key."""
    monkeypatch.setattr(
        simprint_module.sct,
        "gen_text_code_semantic",
        lambda *args, **kwargs: {"features": [{"simprints": []}]},
    )
    result = simprint_module.text_simprints("hello world")
    assert "SEMANTIC_TEXT_V0" not in result


def test_embed_iscc_processing_failure(monkeypatch, tmp_path):
    """Embedding succeeds but ISCC processing of the embedded file fails."""
    monkeypatch.setattr(opts, "media_path", tmp_path)
    media_id = _make_package(tmp_path)
    genfile = tmp_path / "embedded.jpg"
    genfile.write_bytes(b"embedded data")
    monkeypatch.setattr(mixins, "app", _fake_app(FakePool(ValueError("processing failed"))))
    pool = FakePool(str(genfile))
    response = asyncio.run(Metadata().embed(None, media_id, InlineMetadata(name="x"), pool))
    assert response.status == 422
