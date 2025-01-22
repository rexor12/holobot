from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.sdk.wallets.models import ExchangeInfo

class IWalletManager(Protocol):
    def give_money(
        self,
        user_id: int,
        currency_id: int,
        server_id: int,
        amount: int
    ) -> Awaitable[ExchangeInfo]:
        ...

    def take_money(
        self,
        user_id: int,
        currency_id: int,
        server_id: int,
        amount: int,
        allow_take_less: bool
    ) -> Awaitable[ExchangeInfo]:
        ...
