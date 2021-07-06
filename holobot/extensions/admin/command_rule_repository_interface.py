from .models import CommandRule
from typing import Optional, Tuple

class CommandRuleRepositoryInterface:
    async def get(self, id: int) -> Optional[CommandRule]:
        raise NotImplementedError
    
    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> Tuple[CommandRule, ...]:
        raise NotImplementedError
    
    async def add_or_update(self, rule: CommandRule) -> int:
        raise NotImplementedError
