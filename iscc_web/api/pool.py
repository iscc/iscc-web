# -*- coding: utf-8 -*-
from concurrent.futures.process import BrokenProcessPool
from loguru import logger as log
from concurrent.futures import ProcessPoolExecutor
from iscc_web.options import opts


class Pool:
    def __init__(self):
        self._executor = ProcessPoolExecutor(max_workers=opts.max_workers)

    def submit(self, __fn, *args, **kwargs):
        try:
            return self._executor.submit(__fn, *args, **kwargs)
        except BrokenProcessPool as e:
            log.error(f"Failed {__fn} pool execution: {e}", enqueue=True)
            log.info("Restarting pool and retrying", enqueue=True)
            self._executor.shutdown(wait=False, cancel_futures=True)
            self._executor = ProcessPoolExecutor(max_workers=opts.max_workers)
            return self._executor.submit(__fn, *args, **kwargs)

    def shutdown(self, wait=True, *, cancel_futures=False):
        return self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)
