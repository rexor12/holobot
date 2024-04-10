from collections.abc import Awaitable
from typing import Protocol

class IUserProfileManager(Protocol):
    def add_reputation_point(
        self,
        user_id: str
    ) -> Awaitable[int]:
        ...
