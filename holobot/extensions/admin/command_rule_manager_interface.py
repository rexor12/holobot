from typing import Optional, Protocol

from .models import CommandRule
from holobot.sdk.queries import PaginationResult

class CommandRuleManagerInterface(Protocol):
    async def get_rules_by_server(self, server_id: str, page_index: int, page_size: int, group: Optional[str] = None, subgroup: Optional[str] = None) -> PaginationResult[CommandRule]:
        ...

    async def set_rule(self, rule: CommandRule) -> int:
        ...
    
    async def remove_rule(self, rule_id: int) -> None:
        ...
    
    async def remove_rules_by_server(self, server_id: str) -> None:
        ...
    
    async def can_execute(self, server_id: str, channel_id: str, group: Optional[str], subgroup: Optional[str], command: str) -> bool:
        ...
