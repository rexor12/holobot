from .command_interface import CommandInterface
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from typing import Tuple

class CommandBase(CommandInterface):
    def __init__(self, services: ServiceCollectionInterface, name: str) -> None:
        super().__init__()
        debugger = services.get(DebuggerInterface)
        self.group_name = None
        self.subgroup_name = None
        self.name = name if not debugger.is_debug_mode_enabled() else f"d{name}"
        self.description = None
        self.options = []
    
    async def is_allowed_for_guild(self, guild_id: str) -> bool:
        return True

    async def get_allowed_guild_ids(self) -> Tuple[str, ...]:
        return tuple()
