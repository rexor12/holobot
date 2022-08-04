from typing import Any, Dict, Protocol

from holobot.sdk.diagnostics import IExecutionContext

class IExecutionContextFactory(Protocol):
    def create(
        self,
        message: str,
        event_name: str,
        extra_info: Dict[str, Any] | None = None
    ) -> IExecutionContext:
        ...
