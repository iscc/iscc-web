"""Tests for GET /health and the model warm-up readiness state behind it (iscc_web/health.py)."""

import asyncio
from time import sleep, time

import httpx
import onnxruntime as rt

from iscc_web import health
from iscc_web.api.schema import Health
from tests.conftest import private_port, server_host, server_port
from tests.private_server import BUILD_REVISION, BUILD_VERSION
from tests.test_controllers_inprocess import FakePool

CPU = "CPUExecutionProvider"
CUDA = health.CUDA
CPU_BUILD = ["AzureExecutionProvider", CPU]
GPU_BUILD = ["TensorrtExecutionProvider", CUDA, CPU]


def probe(offered, *sessions):
    """Worker probe result as returned by health.probe_models."""
    return {"offered": offered, "sessions": list(sessions)}


def wait_for_ready(port, timeout=120.0):
    """Poll GET /health until the server's model warm-up finished (200) or the timeout passed."""
    deadline = time() + timeout
    response = httpx.get(f"http://{server_host}:{port}/health")
    while response.status_code != 200 and time() < deadline:
        sleep(0.5)
        response = httpx.get(f"http://{server_host}:{port}/health")
    return response


def test_report_before_models_load_is_503():
    status, body = health.report(health.STARTING, "", "")
    assert status == 503
    assert body == {
        "status": "starting",
        "version": None,
        "revision": None,
        "execution_provider": None,
        "models_loaded": False,
    }


def test_report_cpu_build_on_cpu_is_200():
    status, body = health.report(health.assess([probe(CPU_BUILD, CPU, CPU)]), "0.4.0", "1bb0c61")
    assert status == 200
    assert body == {
        "status": "ok",
        "version": "0.4.0",
        "revision": "1bb0c61",
        "execution_provider": CPU,
        "models_loaded": True,
    }


def test_report_gpu_build_on_cuda_is_200():
    probes = [probe(GPU_BUILD, CUDA, CUDA), probe(GPU_BUILD, CUDA, CUDA)]
    status, body = health.report(health.assess(probes), "0.4.0-gpu", "1bb0c61")
    assert status == 200
    assert body["status"] == "ok"
    assert body["execution_provider"] == CUDA


def test_report_cuda_offered_but_session_on_cpu_is_503():
    # One worker's image model fell back to CPU (e.g. CUDA session creation failed).
    probes = [probe(GPU_BUILD, CUDA, CUDA), probe(GPU_BUILD, CUDA, CPU)]
    status, body = health.report(health.assess(probes), "0.4.0-gpu", "1bb0c61")
    assert status == 503
    assert body["status"] == "degraded"
    assert body["execution_provider"] == CPU
    assert body["models_loaded"] is True


def test_report_failed_warm_up_is_503():
    status, body = health.report(health.FAILED, "0.4.0", "1bb0c61")
    assert status == 503
    assert body["status"] == "error"
    assert body["models_loaded"] is False


def test_report_includes_version_and_revision():
    _, body = health.report(health.STARTING, "0.4.0-gpu", "1bb0c619a73069023df02decf529c3d20a0c34ae")
    assert body["version"] == "0.4.0-gpu"
    assert body["revision"] == "1bb0c619a73069023df02decf529c3d20a0c34ae"


def test_load_models_loads_via_probe(monkeypatch):
    calls = []
    monkeypatch.setattr(health, "probe_models", lambda: calls.append("probe"))
    health.load_models()
    assert calls == ["probe"]


def test_load_models_swallows_errors(monkeypatch):
    # An exception escaping a pool initializer would break the whole pool (BrokenProcessPool).
    def fail():
        raise RuntimeError("CUDA session failed")

    monkeypatch.setattr(health, "probe_models", fail)
    health.load_models()


def test_warm_up_fetches_models_before_probing(monkeypatch):
    calls = []
    monkeypatch.setattr(health, "state", dict(health.STARTING))
    monkeypatch.setattr(health, "fetch_models", lambda: calls.append("fetch"))
    pool = FakePool(probe(GPU_BUILD, CUDA, CUDA), probe(GPU_BUILD, CUDA, CUDA))
    original_submit = pool.submit
    monkeypatch.setattr(pool, "submit", lambda fn: calls.append("probe") or original_submit(fn))
    asyncio.run(health.warm_up(pool, 2))
    assert calls == ["fetch", "probe", "probe"]
    assert health.state == {"status": "ok", "models_loaded": True, "execution_provider": CUDA}


def test_warm_up_probe_failure_reports_error(monkeypatch):
    monkeypatch.setattr(health, "state", dict(health.STARTING))
    monkeypatch.setattr(health, "fetch_models", lambda: None)
    asyncio.run(health.warm_up(FakePool(RuntimeError("CUDA session failed")), 1))
    assert health.state == health.FAILED


def test_warm_up_fetch_failure_reports_error(monkeypatch):
    def fail():
        raise OSError("model download failed")

    monkeypatch.setattr(health, "state", dict(health.STARTING))
    monkeypatch.setattr(health, "fetch_models", fail)
    asyncio.run(health.warm_up(FakePool(), 1))
    assert health.state == health.FAILED


def test_get_health_ready():
    response = wait_for_ready(server_port)
    assert response.status_code == 200
    body = response.json()
    Health.model_validate(body)
    expected_provider = CUDA if CUDA in rt.get_available_providers() else CPU
    assert body == {
        "status": "ok",
        "version": None,
        "revision": None,
        "execution_provider": expected_provider,
        "models_loaded": True,
    }


def test_get_health_reports_build_metadata(papi):
    # The private server sets ISCC_WEB_BUILD_VERSION/REVISION like the Docker images do. The fields
    # are present in every state, so there is no need to wait for the warm-up.
    body = httpx.get(f"http://{server_host}:{private_port}/health").json()
    assert body["version"] == BUILD_VERSION
    assert body["revision"] == BUILD_REVISION
