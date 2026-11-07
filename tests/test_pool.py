"""Tests for the self-healing process pool."""

from concurrent.futures.process import BrokenProcessPool

import iscc_web.api.pool as pool_module
from iscc_web.api.pool import Pool


class BrokenExecutor:
    """Stub executor that simulates a broken process pool on submit."""

    def submit(self, fn, *args, **kwargs):
        raise BrokenProcessPool("worker died")

    def shutdown(self, wait=True, cancel_futures=False):
        pass


def models_cached():
    # type: () -> bool
    """Whether this process already holds both ONNX inference sessions (runs in a pool worker)."""
    import iscc_sci.code_semantic_image as image
    import iscc_sct.code_semantic_text as text

    return image._model is not None and text.model.cache_info().currsize == 1


def test_pool_workers_load_models_before_their_first_job(monkeypatch):
    monkeypatch.setattr(pool_module.opts, "max_workers", 1)
    pool = Pool()
    try:
        assert pool.submit(models_cached).result(timeout=120) is True
    finally:
        pool.shutdown(wait=True)


def test_pool_submit(monkeypatch):
    monkeypatch.setattr(pool_module.opts, "max_workers", 1)
    pool = Pool()
    try:
        assert pool.submit(len, "ab").result(timeout=60) == 2
    finally:
        pool.shutdown(wait=True)


def test_pool_restarts_after_broken_process_pool(monkeypatch):
    monkeypatch.setattr(pool_module.opts, "max_workers", 1)
    pool = Pool()
    pool._executor.shutdown(wait=True)
    pool._executor = BrokenExecutor()
    try:
        assert pool.submit(len, "abc").result(timeout=60) == 3
    finally:
        pool.shutdown(wait=True)
