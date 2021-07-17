from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .models import CommandRule
from holobot.sdk.ioc.decorators import injectable
from typing import Optional, Tuple

@injectable(CommandRuleRepositoryInterface)
class CommandRuleRepository(CommandRuleRepositoryInterface):
    async def get(self, id: int) -> Optional[CommandRule]:
        raise NotImplementedError
    
    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> Tuple[CommandRule, ...]:
        raise NotImplementedError
    
    async def add_or_update(self, rule: CommandRule) -> int:
        raise NotImplementedError