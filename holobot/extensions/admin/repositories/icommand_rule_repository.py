from collections.abc import Awaitable, Sequence
from typing import Protocol

from holobot.extensions.admin.models import CommandRule
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class ICommandRuleRepository(
    IRepository[int, CommandRule],
    Protocol
):
    def add_or_update(self, rule: CommandRule) -> Awaitable[int]:
        ...

    def get_many(
        self,
        server_id: str,
        group: str | None,
        subgroup: str | None,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[CommandRule]]:
        ...

    def get_relevant(
        self,
        server_id: str,
        channel_id: str,
        group: str | None,
        subgroup: str | None,
        command: str | None
    ) -> Awaitable[Sequence[CommandRule]]:
        ...

    def delete_by_server(self, server_id: str) -> Awaitable[int]:
        ...
