# -*- coding: utf-8 -*-
from concurrent.futures import ProcessPoolExecutor


class Pool:
    def __init__(self):
        self.executor = ProcessPoolExecutor()
