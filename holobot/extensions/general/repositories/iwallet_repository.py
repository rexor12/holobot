from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models import Wallet, WalletWithDetailsDto
from holobot.extensions.general.sdk.wallets.models import WalletId
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IWalletRepository(IRepository[WalletId, Wallet], Protocol):
    def remove_from_all_users(self, amount: int) -> Awaitable[None]:
        ...

    def get_wallets(
        self,
        user_id: int,
        server_id: int | None = None,
        include_global: bool = False
    ) -> Awaitable[tuple[Wallet, ...]]:
        ...

    def paginate_wallets_with_details(
        self,
        user_id: int,
        server_id: int | None = None,
        include_global: bool = False,
        page_index: int = 0,
        page_size: int = 5
    ) -> Awaitable[PaginationResult[WalletWithDetailsDto]]:
        ...
