from __future__ import annotations
from collections.abc import Sequence
from typing import Any

from .execution_context_data import ExecutionContextData
from .iexecution_context import IExecutionContext
from .stopwatch import Stopwatch

class ExecutionContext(IExecutionContext):
    def __init__(self) -> None:
        self.__events: dict[str, ExecutionContextData] = {}
        self.__stopwatches: dict[str, Stopwatch] = {}
        self.__is_collected: bool = False

    def collect(self) -> Sequence[ExecutionContextData]:
        if self.__stopwatches:
            raise ValueError("One or more events are still being measured.")

        self.__is_collected = True
        return tuple(self.__events.values())

    def start(
        self,
        event_name: str,
        extra_info: dict[str, Any] | None = None
    ) -> Stopwatch:
        if self.__is_collected:
            raise ValueError("New events cannot be tracked once collection has been done.")

        if event_name in self.__stopwatches:
            raise ValueError("A single event type may only be measured once in a single context.")

        if extra_info is None:
            extra_info = {}

        self.__events[event_name] = ExecutionContextData(event_name, extra_infos=extra_info)
        stopwatch = Stopwatch(lambda elapsed_ms: self.__on_event(event_name, elapsed_ms))
        self.__stopwatches[event_name] = stopwatch
        return stopwatch

    def __on_event(self, event_name: str, elapsed_ms: float) -> None:
        self.__events[event_name].elapsed_milliseconds = elapsed_ms
        self.__stopwatches.pop(event_name)

    def _on_dispose(self) -> None:
        return
