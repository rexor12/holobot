from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.enums import RankingType, ReactionType
from holobot.extensions.general.models import Marriage, RankingInfo
from holobot.sdk.queries import PaginationResult

class IMarriageManager(Protocol):
    def get_spouse_id(
        self,
        server_id: str,
        user_id: str
    ) -> Awaitable[str | None]:
        ...

    def marry(
        self,
        server_id: str,
        user_id: str,
        target_user_id: str
    ) -> Awaitable[None]:
        ...

    def divorce(
        self,
        server_id: str,
        user_id: str,
        spouse_id: str
    ) -> Awaitable[None]:
        ...

    def try_add_reaction(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str,
        reaction_type: ReactionType
    ) -> Awaitable[bool]:
        ...

    def get_react_score_bonus(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str,
    ) -> Awaitable[int]:
        ...

    def get_marriage(self, server_id: str, user_id: str) -> Awaitable[Marriage | None]:
        ...

    def get_ranking_infos(
        self,
        server_id: str,
        ranking_type: RankingType,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[RankingInfo]]:
        ...
