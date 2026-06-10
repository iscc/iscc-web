"""Tests for the periodic upload cleanup task."""

import asyncio

import iscc_web as iw
from iscc_web.cleanup import cleanup_task


def _run_cleanup_briefly():
    """Run cleanup_task for a moment, then cancel it (the task loops forever by design)."""

    async def runner():
        task = asyncio.create_task(cleanup_task())
        await asyncio.sleep(0.3)
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

    _run_cleanup_briefly()

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
