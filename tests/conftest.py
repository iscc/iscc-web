# ruff: noqa: E402
import os

# Test environment must be configured BEFORE iscc_web is imported: opts is instantiated at
# import time, and on Linux the server subprocess forks with this module state already loaded.
os.environ["ISCC_WEB_PRIVATE_FILES"] = "false"
# Workers share the media/ directory; disable the periodic cleanup task so parallel servers
# do not race each other deleting expired package dirs.
os.environ["ISCC_WEB_CLEANUP_INTERVAL"] = "0"
# Each xdist worker runs its own server; one iscc worker process per server is enough for
# tests and keeps total memory in check (iscc-sdk imports are heavyweight per process).
os.environ["ISCC_WEB_MAX_WORKERS"] = "1"
# Small enough that tests can exercise the oversize-upload rejection with an in-memory body,
# large enough for all iscc-samples test files.
os.environ["ISCC_WEB_MAX_UPLOAD_SIZE"] = "1000000"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import threading
import multiprocessing
from time import sleep, time
import socket
import pytest
import uvicorn
from iscc_web import app
import httpx

# Server subprocesses must use spawn (Windows' only mode) on every platform: a forked child
# would inherit this process' already-imported iscc_web with its frozen opts instead of
# re-importing under the env configured above (or, for the private server, its own env).
mp = multiprocessing.get_context("spawn")

# Each pytest-xdist worker (gw0, gw1, ...) gets its own server port to avoid bind conflicts.
_worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
_port_offset = int(_worker[2:]) if _worker.startswith("gw") else 0

server_host = "localhost"
server_port = 44555 + _port_offset
server_api_path = "api/v1"
private_port = 44700 + _port_offset


def _start_server(stop_event):
    """Serve the app until stop_event is set, then exit cleanly so coverage data gets flushed."""
    config = uvicorn.Config(app, host=server_host, port=server_port, log_level="debug")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.start()
    stop_event.wait()
    server.should_exit = True
    thread.join()


def wait_for_server(server_process, host=server_host, port=server_port, timeout=30.0):
    """Block until the server accepts TCP connections (or fail fast if the process died)."""
    deadline = time() + timeout
    while time() < deadline:
        if not server_process.is_alive():
            raise RuntimeError(f"The server process did not start! exitcode={server_process.exitcode}")
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            sleep(0.1)
    raise RuntimeError(f"Server on port {port} not reachable after {timeout}s")


@pytest.fixture(scope="session")
def api() -> httpx.Client:
    return httpx.Client(base_url=f"http://{server_host}:{server_port}/{server_api_path}", timeout=None)


@pytest.fixture(scope="session", autouse=True)
def server():
    stop_event = mp.Event()
    server_process = mp.Process(target=_start_server, args=(stop_event,))
    server_process.start()
    wait_for_server(server_process)

    yield 1

    stop_event.set()
    server_process.join(timeout=30)


@pytest.fixture(scope="session")
def papi():
    """Client against a server running with ISCC_WEB_PRIVATE_FILES=true and CORS enabled."""
    from tests import private_server

    stop_event = mp.Event()
    process = mp.Process(target=private_server.run, args=(server_host, private_port, stop_event))
    process.start()
    wait_for_server(process, port=private_port)
    client = httpx.Client(base_url=f"http://{server_host}:{private_port}/{server_api_path}", timeout=None)
    yield client
    client.close()
    stop_event.set()
    process.join(timeout=30)
