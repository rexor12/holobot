from .command_interface import CommandInterface
from typing import Tuple

class CommandBase(CommandInterface):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.options = []
    
    async def is_allowed_for_guild(self, guild_id: str) -> bool:
        return True

    async def get_allowed_guild_ids(self) -> Tuple[str, ...]:
        return tuple()
