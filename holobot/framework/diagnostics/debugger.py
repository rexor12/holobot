from holobot.framework.configs import EnvironmentOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.diagnostics import IDebugger
from holobot.sdk.ioc.decorators import injectable

@injectable(IDebugger)
class Debugger(IDebugger):
    def __init__(self, options: IOptions[EnvironmentOptions]) -> None:
        super().__init__()
        self.__options = options

    def is_debug_mode_enabled(self) -> bool:
        return self.__options.value.IsDebug
