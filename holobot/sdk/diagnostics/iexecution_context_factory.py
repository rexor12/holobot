from typing import Any, Protocol

from holobot.sdk.diagnostics import IExecutionContext

class IExecutionContextFactory(Protocol):
    def create(
        self,
        message: str,
        event_name: str,
        extra_info: dict[str, Any] | None = None
    ) -> IExecutionContext:
        ...
