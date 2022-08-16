from collections.abc import Sequence
from typing import Protocol

from .models import CommandRule
from holobot.sdk.queries import PaginationResult

class CommandRuleRepositoryInterface(Protocol):
    async def add_or_update(self, rule: CommandRule) -> int:
        ...

    async def get(self, id: int) -> CommandRule | None:
        ...

    async def get_many(self, server_id: str, group: str | None, subgroup: str | None, page_index: int, page_size: int) -> PaginationResult[CommandRule]:
        ...

    async def get_relevant(self, server_id: str, channel_id: str, group: str | None, subgroup: str | None, command: str | None) -> Sequence[CommandRule]:
        ...

    async def delete_by_id(self, rule_id: int) -> None:
        ...

    async def delete_by_server(self, server_id: str) -> None:
        ...
