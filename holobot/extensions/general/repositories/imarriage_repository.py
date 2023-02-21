from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.enums import RankingType
from holobot.extensions.general.models import Marriage, RankingInfo
from holobot.sdk.database.queries.enums import Order
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IMarriageRepository(IRepository[int, Marriage], Protocol):
    def get_by_user(
        self,
        server_id: str,
        user_id: str
    ) -> Awaitable[Marriage | None]:
        ...

    def get_by_users(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str
    ) -> Awaitable[Marriage | None]:
        ...

    def delete_by_user(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str
    ) -> Awaitable[bool]:
        ...

    def paginate_rankings(
        self,
        server_id: str,
        ranking_type: RankingType,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[RankingInfo]]:
        ...
