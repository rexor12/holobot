from typing import Protocol

from PIL.Image import Image

from holobot.extensions.general.models.user_profiles import UserProfile

class IUserProfileFactory(Protocol):
    def create_profile_image(
        self,
        user_name: str,
        user_profile: UserProfile,
        avatar: bytes | None,
        custom_background_code: str | None = None
    ) -> bytes:
        ...
