from typing import Protocol

from ..enums import Permission
from .models import MemberData

class IMemberDataProvider(Protocol):
    async def get_basic_data_by_id(
        self,
        server_id: str,
        user_id: str
    ) -> MemberData:
        ...

    async def get_basic_data_by_name(
        self,
        server_id: str,
        name: str
    ) -> MemberData:
        ...

    def is_member(self, server_id: str, user_id: str) -> bool:
        ...

    def get_member_permissions(
        self,
        server_id: str,
        channel_id: str,
        user_id: str
    ) -> Permission:
        ...
