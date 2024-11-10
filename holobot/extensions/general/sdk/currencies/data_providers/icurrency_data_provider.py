from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.sdk.currencies.models import ICurrency

class ICurrencyDataProvider(Protocol):
    def get_currency_by_code(self, server_id: int, code: str) -> Awaitable[ICurrency | None]:
        ...
