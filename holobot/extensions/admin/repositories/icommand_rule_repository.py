from collections.abc import Sequence
from typing import Protocol

from holobot.extensions.admin.models import CommandRule
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class ICommandRuleRepository(
    IRepository[int, CommandRule],
    Protocol
):
    async def add_or_update(self, rule: CommandRule) -> int:
        ...

    async def get_many(
        self,
        server_id: str,
        group: str | None,
        subgroup: str | None,
        page_index: int,
        page_size: int
    ) -> PaginationResult[CommandRule]:
        ...

    async def get_relevant(
        self,
        server_id: str,
        channel_id: str,
        group: str | None,
        subgroup: str | None,
        command: str | None
    ) -> Sequence[CommandRule]:
        ...

    async def delete_by_server(self, server_id: str) -> None:
        ...
