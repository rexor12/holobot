from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.enums import RankingType
from holobot.extensions.general.models import Marriage, RankingInfo
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IMarriageRepository(IRepository[int, Marriage], Protocol):
    def get_by_user(
        self,
        server_id: int,
        user_id: int
    ) -> Awaitable[Marriage | None]:
        ...

    def get_by_users(
        self,
        server_id: int,
        user_id1: int,
        user_id2: int
    ) -> Awaitable[Marriage | None]:
        ...

    def delete_by_user(
        self,
        server_id: int,
        user_id1: int,
        user_id2: int
    ) -> Awaitable[bool]:
        ...

    def paginate_rankings(
        self,
        server_id: int,
        ranking_type: RankingType,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[RankingInfo]]:
        ...
