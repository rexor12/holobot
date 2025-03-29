from collections.abc import Awaitable, Sequence
from typing import Protocol

from holobot.extensions.general.models.items import BackgroundDisplayInfo
from holobot.extensions.general.models.user_profiles import UserProfileBackground
from holobot.sdk.database.repositories import IRepository

class IUserProfileBackgroundRepository(IRepository[int, UserProfileBackground], Protocol):
    def get_by_code(self, background_code: str) -> Awaitable[UserProfileBackground | None]:
        ...

    def get_code(self, background_id: int) -> Awaitable[str | None]:
        ...

    def get_id_by_code(self, code: str) -> Awaitable[int | None]:
        ...

    def get_name_by_code(self, code: str) -> Awaitable[str | None]:
        ...

    def get_display_info(
        self,
        background_id: int
    ) -> Awaitable[BackgroundDisplayInfo]:
        ...

    def get_display_infos(
        self,
        background_ids: Sequence[int]
    ) -> Awaitable[list[BackgroundDisplayInfo]]:
        ...
