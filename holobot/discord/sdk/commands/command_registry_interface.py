from .command_descriptor import CommandDescriptor
from typing import Optional

class CommandRegistryInterface:
    async def register(self, command: CommandDescriptor) -> None:
        raise NotImplementedError
    
    async def command_exists(self, name: str, group: Optional[str] = None, sub_group: Optional[str] = None) -> bool:
        raise NotImplementedError
    
    async def group_exists(self, group: str) -> bool:
        raise NotImplementedError
