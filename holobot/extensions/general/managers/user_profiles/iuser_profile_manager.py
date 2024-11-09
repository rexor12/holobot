from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.user_profiles import ReputationChangeInfo, UserProfile

class IUserProfileManager(Protocol):
    def add_reputation_point(
        self,
        user_id: int
    ) -> Awaitable[ReputationChangeInfo]:
        ...

    def get_or_create(self, user_id: int) -> Awaitable[UserProfile]:
        ...
