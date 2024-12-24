from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.user_profiles import UserProfile

class IUserProfileFactory(Protocol):
    def create_profile_image(
        self,
        user_name: str,
        user_profile: UserProfile,
        avatar: bytes | None,
        custom_background_code: str | None = None
    ) -> Awaitable[bytes]:
        ...
