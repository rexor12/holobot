from collections.abc import AsyncIterable, Awaitable, Iterable
from typing import Protocol

from ..enums import Permission
from .models import MemberData

class IMemberDataProvider(Protocol):
    def get_basic_data_by_id(
        self,
        server_id: int,
        user_id: int
    ) -> Awaitable[MemberData]:
        ...

    def try_get_basic_data_by_id(
        self,
        server_id: int,
        user_id: int
    ) -> Awaitable[MemberData | None]:
        ...

    def get_basic_data_by_ids(
        self,
        server_id: int,
        user_ids: Iterable[int]
    ) -> AsyncIterable[MemberData]:
        ...

    def get_basic_data_by_name(
        self,
        server_id: int,
        name: str
    ) -> Awaitable[MemberData]:
        ...

    def is_member(self, server_id: int, user_id: int) -> Awaitable[bool]:
        ...

    def get_member_permissions(
        self,
        server_id: int,
        channel_id: int,
        user_id: int
    ) -> Awaitable[Permission]:
        ...
