"""Tests for application wiring in iscc_web.main and the ASGI entrypoint."""

import asyncio

import iscc_web.main as main_module
from iscc_web.asgi import application


def test_asgi_application_is_app():
    assert application is main_module.app


def test_main_invokes_uvicorn(monkeypatch):
    calls = {}

    def fake_run(app, **kwargs):
        calls["app"] = app
        calls.update(kwargs)

    monkeypatch.setattr(main_module.uvicorn, "run", fake_run)
    main_module.main()
    assert calls["app"] == "iscc_web.main:app"
    assert calls["host"] == "localhost"
    assert calls["port"] == 8000
    assert calls["reload"] is True  # test process runs with the default development environment


def test_configure_cleanup_installs_task(monkeypatch, tmp_path):
    monkeypatch.setattr(main_module.opts, "cleanup_interval", 600)
    monkeypatch.setattr(main_module.opts, "media_path", tmp_path)

    async def runner():
        await main_module.configure_cleanup(None)
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        assert len(tasks) == 1
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    asyncio.run(runner())
