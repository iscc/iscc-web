"""Tests for the periodic upload cleanup task."""

import asyncio
import time

import iscc_web as iw
from iscc_web.cleanup import cleanup_task


def _run_cleanup_briefly(until=None, timeout=0.3):
    """
    Run cleanup_task until `until()` is true or `timeout` seconds passed, then cancel it (the task
    loops forever by design). Polling instead of a fixed sleep keeps the test reliable when the
    machine is busy, e.g. while the test servers load their ONNX models.
    """

    async def runner():
        task = asyncio.create_task(cleanup_task())
        deadline = time.monotonic() + timeout
        while not (until and until()) and time.monotonic() < deadline:
            await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(runner())


def test_cleanup_deletes_expired_packages(monkeypatch, tmp_path):
    fixture = tmp_path / "061knt35ejv6o"
    fixture.mkdir()
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*\n")
    expired = tmp_path / "0aaaaaaaaaaaa"
    expired.mkdir()
    monkeypatch.setattr(iw.opts, "media_path", tmp_path)
    monkeypatch.setattr(iw.opts, "storage_expiry", -1)
    monkeypatch.setattr(iw.opts, "cleanup_interval", 0)

    _run_cleanup_briefly(until=lambda: not expired.exists(), timeout=30)

    assert not expired.exists()
    assert fixture.exists()
    assert gitignore.exists()


def test_cleanup_keeps_fresh_packages(monkeypatch, tmp_path):
    fresh = tmp_path / "0bbbbbbbbbbbb"
    fresh.mkdir()
    monkeypatch.setattr(iw.opts, "media_path", tmp_path)
    monkeypatch.setattr(iw.opts, "storage_expiry", 3600)
    monkeypatch.setattr(iw.opts, "cleanup_interval", 0)

    _run_cleanup_briefly()

    assert fresh.exists()
