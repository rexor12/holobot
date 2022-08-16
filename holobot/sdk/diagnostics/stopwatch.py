from __future__ import annotations
from collections.abc import Callable

import time

from holobot.sdk import IDisposable

class Stopwatch(IDisposable):
    def __init__(
        self,
        on_stop: Callable[[float], None]
    ) -> None:
        self.__on_stop = on_stop
        self.__is_running = True
        self.__start_time = time.perf_counter()

    def __enter__(self) -> Stopwatch:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def stop(self) -> None:
        if not self.__is_running:
            return
        self.__on_stop((time.perf_counter() - self.__start_time) * 1000)
        self.__is_running = False

    def _on_dispose(self) -> None:
        self.stop()
