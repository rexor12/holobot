from .models import CommandRule
from typing import Optional, Tuple

class CommandRuleManagerInterface:
    async def get_rules_by_server(self, server_id: str, start_offset: int, page_size: int) -> Tuple[CommandRule, ...]:
        raise NotImplementedError

    async def set_rule(self, rule: CommandRule) -> int:
        raise NotImplementedError
    
    async def remove_rule(self, rule_id: int) -> None:
        raise NotImplementedError
    
    async def can_execute(self, server_id: str, channel_id: str, group: Optional[str], subgroup: Optional[str], command: str) -> bool:
        raise NotImplementedError
