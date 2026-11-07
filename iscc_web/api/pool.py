# -*- coding: utf-8 -*-
from concurrent.futures.process import BrokenProcessPool
from loguru import logger as log
from concurrent.futures import ProcessPoolExecutor
from iscc_web.health import load_models
from iscc_web.options import opts


def new_executor():
    # type: () -> ProcessPoolExecutor
    """Process pool whose workers load the ONNX models before taking their first job."""
    return ProcessPoolExecutor(max_workers=opts.max_workers, initializer=load_models)


class Pool:
    def __init__(self):
        self._executor = new_executor()

    def submit(self, __fn, *args, **kwargs):
        try:
            return self._executor.submit(__fn, *args, **kwargs)
        except BrokenProcessPool as e:
            log.error(f"Failed {__fn} pool execution: {e}", enqueue=True)
            log.info("Restarting pool and retrying", enqueue=True)
            self._executor.shutdown(wait=False, cancel_futures=True)
            self._executor = new_executor()
            return self._executor.submit(__fn, *args, **kwargs)

    @property
    def max_workers(self):
        # type: () -> int
        """Number of worker processes the pool runs at most (resolved by the executor)."""
        return self._executor._max_workers

    def shutdown(self, wait=True, *, cancel_futures=False):
        return self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)
