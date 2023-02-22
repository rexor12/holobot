from collections.abc import AsyncIterable, Awaitable, Iterable
from typing import Protocol

from ..enums import Permission
from .models import MemberData

class IMemberDataProvider(Protocol):
    def get_basic_data_by_id(
        self,
        server_id: str,
        user_id: str
    ) -> Awaitable[MemberData]:
        ...

    def get_basic_data_by_ids(
        self,
        server_id: str,
        user_ids: Iterable[str]
    ) -> AsyncIterable[MemberData]:
        ...

    def get_basic_data_by_name(
        self,
        server_id: str,
        name: str
    ) -> Awaitable[MemberData]:
        ...

    def is_member(self, server_id: str, user_id: str) -> Awaitable[bool]:
        ...

    def get_member_permissions(
        self,
        server_id: str,
        channel_id: str,
        user_id: str
    ) -> Awaitable[Permission]:
        ...
