from typing import Any, Callable, Sequence

from holobot.sdk.diagnostics import ExecutionContextData, IExecutionContext, Stopwatch

class ExecutionContextWrapper(IExecutionContext):
    def __init__(
        self,
        context: IExecutionContext,
        on_dispose: Callable[[], None]
    ) -> None:
        super().__init__()
        self.__context = context
        self.__on_dispose = on_dispose

    def collect(self) -> Sequence[ExecutionContextData]:
        return self.__context.collect()

    def start(
        self,
        event_name: str,
        extra_info: dict[str, Any] | None = None
    ) -> Stopwatch:
        return self.__context.start(event_name, extra_info)

    def _on_dispose(self) -> None:
        self.__on_dispose()
