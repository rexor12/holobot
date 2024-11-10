from collections.abc import Awaitable
from typing import Protocol

from holobot.discord.sdk.models import Role

class IRoleManager(Protocol):
    def get_role(self, server_id: int, role_name: str) -> Role | None:
        ...

    def create_role(self, server_id: int, role_name: str, description: str) -> Awaitable[Role]:
        ...
