from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.user_profiles import ReputationChangeInfo

class IUserProfileManager(Protocol):
    def add_reputation_point(
        self,
        user_id: str
    ) -> Awaitable[ReputationChangeInfo]:
        ...
