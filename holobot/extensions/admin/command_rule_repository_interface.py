from typing import Optional, Protocol, Sequence

from .models import CommandRule
from holobot.sdk.queries import PaginationResult

class CommandRuleRepositoryInterface(Protocol):
    async def add_or_update(self, rule: CommandRule) -> int:
        ...
    
    async def get(self, id: int) -> Optional[CommandRule]:
        ...
    
    async def get_many(self, server_id: str, group: Optional[str], subgroup: Optional[str], page_index: int, page_size: int) -> PaginationResult[CommandRule]:
        ...
    
    async def get_relevant(self, server_id: str, channel_id: str, group: Optional[str], subgroup: Optional[str], command: Optional[str]) -> Sequence[CommandRule]:
        ...
    
    async def delete_by_id(self, rule_id: int) -> None:
        ...
    
    async def delete_by_server(self, server_id: str) -> None:
        ...
