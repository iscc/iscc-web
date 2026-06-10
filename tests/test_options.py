"""Tests for application settings and sentry initialization."""

import importlib

import iscc_web.options


def test_debug_property():
    assert iscc_web.options.IsccWebOptions(environment="development").debug is True
    assert iscc_web.options.IsccWebOptions(environment="production").debug is False


def test_sentry_init_with_dsn(monkeypatch):
    monkeypatch.setenv("ISCC_WEB_SENTRY_DSN", "https://examplePublicKey@o0.ingest.sentry.io/0")
    module = importlib.reload(iscc_web.options)
    assert module.opts.sentry_dsn == "https://examplePublicKey@o0.ingest.sentry.io/0"
    # Restore the module-level opts built without a DSN.
    monkeypatch.delenv("ISCC_WEB_SENTRY_DSN")
    module = importlib.reload(iscc_web.options)
    assert module.opts.sentry_dsn == ""
