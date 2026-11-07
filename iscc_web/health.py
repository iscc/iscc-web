# -*- coding: utf-8 -*-
"""
Service readiness for `GET /health`.

Every ISCC worker process loads the iscc-sct and iscc-sci ONNX models in its initializer, before
it takes its first job, so no request reaches a cold worker. At startup the service starts all
workers and records which execution provider their inference sessions run on. `/health` answers
from that cached state - no inference and no pool round trip per request.

Ready means the models are loaded and, if the installed onnxruntime build offers CUDA, every
model session actually runs on CUDA. A GPU image whose sessions fell back to CPU (onnxruntime
does that silently, e.g. after NVIDIA driver drift) keeps serving, but slowly - it reports
`degraded`.
"""

import asyncio
import time

from loguru import logger as log

CUDA = "CUDAExecutionProvider"
STARTING = {"status": "starting", "models_loaded": False, "execution_provider": None}
FAILED = {"status": "error", "models_loaded": False, "execution_provider": None}

# Readiness verdict for /health - STARTING until the model warm-up finishes.
state = dict(STARTING)


def probe_models():
    # type: () -> dict
    """
    Load the iscc-sct and iscc-sci ONNX models and report their execution providers.

    Runs in a pool worker. Both libraries cache their inference session per process, so the probe
    also warms the worker for semantic requests.
    """
    import onnxruntime as rt
    from iscc_sci.code_semantic_image import model as image_model
    from iscc_sct.code_semantic_text import model as text_model

    sessions = [text_model().get_providers()[0], image_model().get_providers()[0]]
    return {"offered": rt.get_available_providers(), "sessions": sessions}


def load_models():
    # type: () -> None
    """
    Pool worker initializer: load the ONNX models before the worker takes its first job.

    Failures are only logged - an exception here would break the whole pool. The worker then
    retries the load on its next semantic job, and a warm-up probe it runs reports the error.
    """
    try:
        probe_models()
    except Exception:
        log.exception("Loading the ONNX models in a pool worker failed")


def fetch_models():
    # type: () -> None
    """Download missing iscc-sct/iscc-sci ONNX model files (existing files are only checksum-verified)."""
    import iscc_sci.utils
    import iscc_sct.utils

    iscc_sct.utils.get_model()
    iscc_sci.utils.get_model()


def assess(probes):
    # type: (list[dict]) -> dict
    """
    Derive the readiness verdict from worker probes.

    `degraded` if any model session runs on a provider other than CUDA although the onnxruntime
    build offers CUDA. `execution_provider` is the slowest provider any session runs on.
    """
    sessions = [provider for probe in probes for provider in probe["sessions"]]
    fallback = [provider for provider in sessions if provider != CUDA]
    cuda_offered = any(CUDA in probe["offered"] for probe in probes)
    status = "degraded" if cuda_offered and fallback else "ok"
    return {"status": status, "models_loaded": True, "execution_provider": fallback[0] if fallback else CUDA}


async def warm_up(pool, workers):
    # type: (Pool, int) -> None
    """Load the models in `workers` pool workers concurrently and record the verdict in `state`."""
    loop = asyncio.get_running_loop()
    start = time.perf_counter()
    try:
        # Fetch first, once: the libraries download straight into the final model path without
        # locking, so parallel probes on a fresh install could load a partially written file.
        await asyncio.to_thread(fetch_models)
        probes = await asyncio.gather(*(loop.run_in_executor(pool, probe_models) for _ in range(workers)))
    except Exception:
        log.exception("Model warm-up failed")
        state.update(FAILED)
        return
    state.update(assess(probes))
    seconds = time.perf_counter() - start
    log.info(
        f"Models loaded in {workers} worker(s) in {seconds:.1f}s on {state['execution_provider']}: {state['status']}"
    )


def report(health, version, revision):
    # type: (dict, str, str) -> tuple[int, dict]
    """Status code and JSON body for `GET /health` (empty build metadata of local builds maps to null)."""
    body = {
        "status": health["status"],
        "version": version or None,
        "revision": revision or None,
        "execution_provider": health["execution_provider"],
        "models_loaded": health["models_loaded"],
    }
    return 200 if health["status"] == "ok" else 503, body
