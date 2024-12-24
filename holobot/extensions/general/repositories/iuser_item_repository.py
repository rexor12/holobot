from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models.items import UserItem, WalletWithDetailsDto
from holobot.extensions.general.models.user_profiles import UserProfileBackgroundInfo
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IUserItemRepository(IRepository[UserItemId, UserItem], Protocol):
    #region Backgrounds

    def paginate_backgrounds(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[UserItem]]:
        ...

    def background_exists(
        self,
        user_id: int,
        background_id: int
    ) -> Awaitable[bool]:
        ...

    def paginate_background_infos(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[UserProfileBackgroundInfo]]:
        ...

    #endregion

    #region Badges

    def paginate_badges(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[UserItem]]:
        ...

    def badge_exists(
        self,
        server_id: int,
        user_id: int,
        badge_id: int
    ) -> Awaitable[bool]:
        ...

    #endregion

    #region Currencies

    def get_wallet(
        self,
        user_id: int,
        server_id: int,
        currency_id: int
    ) -> Awaitable[UserItem | None]:
        ...

    def get_wallets(
        self,
        user_id: int,
        server_id: int,
        include_global: bool = False
    ) -> Awaitable[tuple[UserItem, ...]]:
        ...

    def paginate_wallets_with_details(
        self,
        user_id: int,
        server_id: int,
        include_global: bool = False,
        page_index: int = 0,
        page_size: int = 5
    ) -> Awaitable[PaginationResult[WalletWithDetailsDto]]:
        ...

    #endregion
