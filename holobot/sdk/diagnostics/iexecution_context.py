from collections.abc import Sequence
from typing import Any, Protocol

from holobot.sdk import IDisposable
from .execution_context_data import ExecutionContextData
from .stopwatch import Stopwatch

class IExecutionContext(IDisposable, Protocol):
    def collect(self) -> Sequence[ExecutionContextData]:
        ...

    def start(
        self,
        event_name: str,
        extra_info: dict[str, Any] | None = None
    ) -> Stopwatch:
        ...
