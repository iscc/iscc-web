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
