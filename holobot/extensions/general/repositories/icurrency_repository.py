from collections.abc import Awaitable, Iterable
from typing import Protocol

from holobot.extensions.general.models import Currency
from holobot.extensions.general.sdk.currencies.data_providers import ICurrencyDataProvider
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class ICurrencyRepository(IRepository[int, Currency], ICurrencyDataProvider, Protocol):
    def paginate_by_server(
        self,
        server_id: str,
        page_index: int,
        page_size: int,
        include_global: bool
    ) -> Awaitable[PaginationResult[Currency]]:
        ...

    def count_by_server(self, server_id: str) -> Awaitable[int]:
        ...

    def delete_by_server(self, currency_id: int, server_id: str) -> Awaitable[int]:
        ...

    def try_get_by_server(
        self,
        currency_id: int,
        server_id: str,
        allow_global: bool
    ) -> Awaitable[Currency | None]:
        ...

    def search(
        self,
        text: str,
        server_id: str,
        max_count: int,
        include_global: bool
    ) -> Awaitable[Iterable[tuple[int, str]]]:
        ...
