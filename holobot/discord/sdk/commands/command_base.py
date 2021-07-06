from .command_interface import CommandInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.system import EnvironmentInterface
from typing import Tuple

class CommandBase(CommandInterface):
    def __init__(self, services: ServiceCollectionInterface, name: str) -> None:
        super().__init__()
        environment = services.get(EnvironmentInterface)
        self.name = name if not environment.is_debug_mode else f"d{name}"
        self.options = []
    
    async def is_allowed_for_guild(self, guild_id: str) -> bool:
        return True

    async def get_allowed_guild_ids(self) -> Tuple[str, ...]:
        return tuple()
