from collections.abc import Awaitable, Iterable, Sequence
from typing import Protocol

from holobot.extensions.general.models import Currency
from holobot.extensions.general.models.items import CurrencyDisplayInfo
from holobot.extensions.general.sdk.currencies.data_providers import ICurrencyDataProvider
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class ICurrencyRepository(IRepository[int, Currency], ICurrencyDataProvider, Protocol):
    def paginate_by_server(
        self,
        server_id: int,
        page_index: int,
        page_size: int,
        include_global: bool
    ) -> Awaitable[PaginationResult[Currency]]:
        ...

    def count_by_server(self, server_id: int) -> Awaitable[int]:
        ...

    def delete_by_server(self, currency_id: int, server_id: int) -> Awaitable[int]:
        ...

    def try_get_by_server(
        self,
        currency_id: int,
        server_id: int,
        allow_global: bool
    ) -> Awaitable[Currency | None]:
        ...

    def search(
        self,
        text: str,
        server_id: int,
        max_count: int,
        include_global: bool
    ) -> Awaitable[Iterable[tuple[int, str]]]:
        ...

    def get_display_info(
        self,
        currency_id: int
    ) -> Awaitable[CurrencyDisplayInfo]:
        ...

    def get_display_infos(
        self,
        currency_ids: Sequence[int]
    ) -> Awaitable[list[CurrencyDisplayInfo]]:
        ...
