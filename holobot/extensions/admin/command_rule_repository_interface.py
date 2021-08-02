from .models import CommandRule
from typing import Optional, Tuple

class CommandRuleRepositoryInterface:
    async def add_or_update(self, rule: CommandRule) -> int:
        raise NotImplementedError
    
    async def get(self, id: int) -> Optional[CommandRule]:
        raise NotImplementedError
    
    async def get_many(self, server_id: str, start_offset: int, page_size: int) -> Tuple[CommandRule, ...]:
        raise NotImplementedError
    
    async def get_relevant(self, server_id: str, channel_id: str, group: Optional[str], subgroup: Optional[str], command: Optional[str]) -> Tuple[CommandRule, ...]:
        raise NotImplementedError
    
    async def delete_by_id(self, rule_id: int) -> None:
        raise NotImplementedError
