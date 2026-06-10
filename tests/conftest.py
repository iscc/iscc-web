from multiprocessing import Process
from time import sleep, time
import socket
import pytest
import uvicorn
from iscc_web import app
import httpx
import os

# Each pytest-xdist worker (gw0, gw1, ...) gets its own server port to avoid bind conflicts.
_worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
_port_offset = int(_worker[2:]) if _worker.startswith("gw") else 0

server_host = "localhost"
server_port = 44555 + _port_offset
server_api_path = "api/v1"

os.environ["ISCC_WEB_PRIVATE_FILES"] = "false"
# Workers share the media/ directory; disable the periodic cleanup task so parallel servers
# do not race each other deleting expired package dirs.
os.environ["ISCC_WEB_CLEANUP_INTERVAL"] = "0"
# Each xdist worker runs its own server; one iscc worker process per server is enough for
# tests and keeps total memory in check (iscc-sdk imports are heavyweight per process).
os.environ["ISCC_WEB_MAX_WORKERS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"


def _start_server():
    uvicorn.run(app, host=server_host, port=server_port, log_level="debug")


def _wait_for_server(server_process, timeout=30.0):
    """Block until the server accepts TCP connections (or fail fast if the process died)."""
    deadline = time() + timeout
    while time() < deadline:
        if not server_process.is_alive():
            raise RuntimeError(f"The server process did not start! exitcode={server_process.exitcode}")
        try:
            with socket.create_connection((server_host, server_port), timeout=1):
                return
        except OSError:
            sleep(0.1)
    raise RuntimeError(f"Server on port {server_port} not reachable after {timeout}s")


@pytest.fixture(scope="session")
def api() -> httpx.Client:
    return httpx.Client(base_url=f"http://{server_host}:{server_port}/{server_api_path}", timeout=None)


@pytest.fixture(scope="session", autouse=True)
def server():
    server_process = Process(target=_start_server)
    server_process.start()
    _wait_for_server(server_process)

    yield 1

    sleep(1.2)
    server_process.terminate()
