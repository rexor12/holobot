from typing import Protocol

from holobot.sdk.queries import PaginationResult
from .models import CommandRule

class CommandRuleManagerInterface(Protocol):
    async def get_rules_by_server(self, server_id: str, page_index: int, page_size: int, group: str | None = None, subgroup: str | None = None) -> PaginationResult[CommandRule]:
        ...

    async def set_rule(self, rule: CommandRule) -> int:
        ...

    async def remove_rule(self, rule_id: int) -> None:
        ...

    async def remove_rules_by_server(self, server_id: str) -> None:
        ...

    async def can_execute(self, server_id: str, channel_id: str, group: str | None, subgroup: str | None, command: str) -> bool:
        ...
