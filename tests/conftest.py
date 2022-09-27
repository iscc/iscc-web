from multiprocessing import Process
from time import sleep
import pytest
import uvicorn
from iscc_web import app
import httpx
import os

os.environ["ISCC_WEB_SCHEME"] = "http"
os.environ["ISCC_WEB_HOST"] = "localhost"
os.environ["ISCC_WEB_PORT"] = "44555"
os.environ["ISCC_WEB_PRIVATE_FILES"] = "false"


server_host = "localhost"
server_port = 44555
server_api_path = "api/v1"


def get_sleep_time():
    # when starting a server process,
    # a longer sleep time is necessary on Windows
    if os.name == "nt":
        return 1.5
    return 0.5


def _start_server():
    uvicorn.run(app, host=server_host, port=server_port, log_level="debug")


@pytest.fixture(scope="session")
def api() -> httpx.Client:
    return httpx.Client(
        base_url=f"http://{server_host}:{server_port}/{server_api_path}", timeout=None
    )


@pytest.fixture(scope="session", autouse=True)
def server():
    server_process = Process(target=_start_server)
    server_process.start()
    sleep(get_sleep_time())

    if not server_process.is_alive():
        raise TypeError("The server process did not start!")

    yield 1

    sleep(1.2)
    server_process.terminate()
