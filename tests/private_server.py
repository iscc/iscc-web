"""Entry point for a test server with ISCC_WEB_PRIVATE_FILES, CORS and build metadata enabled.

Covers the non-default configuration branches (see test_api_private.py, test_api_cors.py and
test_health.py) without spawning a third server. Lives in its own module so the multiprocessing
child imports it (and nothing else) on spawn - the env vars must be set before iscc_web is imported.
"""

import os
import threading

import uvicorn

CORS_ORIGIN = "https://app.example.com"
BUILD_VERSION = "0.0.0-test"
BUILD_REVISION = "0123456789abcdef0123456789abcdef01234567"


def run(host, port, stop_event):
    """Serve the app with private file access, CORS and build metadata until stop_event is set, then exit cleanly."""
    os.environ["ISCC_WEB_PRIVATE_FILES"] = "true"
    os.environ["ISCC_WEB_CORS_ORIGINS"] = CORS_ORIGIN
    os.environ["ISCC_WEB_BUILD_VERSION"] = BUILD_VERSION
    os.environ["ISCC_WEB_BUILD_REVISION"] = BUILD_REVISION
    os.environ["ISCC_WEB_CLEANUP_INTERVAL"] = "0"
    os.environ["ISCC_WEB_MAX_WORKERS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    from iscc_web import app

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.start()
    stop_event.wait()
    server.should_exit = True
    thread.join()
