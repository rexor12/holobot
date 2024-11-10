from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.mudada.models import Wallet
from holobot.sdk.database.repositories import IRepository

class IWalletRepository(IRepository[int, Wallet], Protocol):
    def remove_from_all_users(self, amount: int) -> Awaitable[None]:
        ...
