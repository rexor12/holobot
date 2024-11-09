from collections.abc import Awaitable
from typing import Protocol

class IWalletManager(Protocol):
    def give_money(
        self,
        user_id: int,
        currency_id: int,
        server_id: int | None,
        amount: int
    ) -> Awaitable[None]:
        ...

    def take_money(
        self,
        user_id: int,
        currency_id: int,
        server_id: int | None,
        amount: int,
        allow_take_less: bool
    ) -> Awaitable[None]:
        ...
