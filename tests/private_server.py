"""Entry point for a test server with ISCC_WEB_PRIVATE_FILES enabled (see test_api_private.py).

Lives in its own module so the multiprocessing child imports it (and nothing else) on spawn -
the private-files env vars must be set before iscc_web is imported.
"""

import os
import threading

import uvicorn


def run(host, port, stop_event):
    """Serve the app with private file access until stop_event is set, then exit cleanly."""
    os.environ["ISCC_WEB_PRIVATE_FILES"] = "true"
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
