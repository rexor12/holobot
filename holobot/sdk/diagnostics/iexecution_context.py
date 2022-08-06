from typing import Any, Dict, Protocol, Sequence

from .execution_context_data import ExecutionContextData
from .stopwatch import Stopwatch
from holobot.sdk import IDisposable

class IExecutionContext(IDisposable, Protocol):
    def collect(self) -> Sequence[ExecutionContextData]:
        ...

    def start(
        self,
        event_name: str,
        extra_info: Dict[str, Any] | None = None
    ) -> Stopwatch:
        ...