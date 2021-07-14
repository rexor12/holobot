from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.ioc.decorators import injectable

@injectable(DebuggerInterface)
class Debugger(DebuggerInterface):
    def __init__(self, configurator: ConfiguratorInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator

    def is_debug_mode_enabled(self) -> bool:
        return self.__configurator.get("General", "IsDebug", False)
