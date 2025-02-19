from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.mudada.models import Transaction
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class ITransactionRepository(IRepository[int, Transaction], Protocol):
    def get_by_users(self, owner_id: int, target_id: int) -> Awaitable[Transaction | None]:
        ...

    def get_total_transaction_amount(
        self,
        owner_id: int,
        include_finalized: bool
    ) -> Awaitable[int]:
        ...

    def delete_all_by_user(self, owner_id: int, delete_finalized: bool) -> Awaitable[int]:
        ...

    def paginate_by_owner(
        self,
        owner_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[Transaction]]:
        ...

    def paginate_by_target(
        self,
        target_id: int,
        page_index: int,
        page_size: int,
        finalized_only: bool
    ) -> Awaitable[PaginationResult[Transaction]]:
        ...

    def get_finalized_uncompleted_by_target(
        self,
        target_id: int
    ) -> Awaitable[tuple[Transaction, ...]]:
        ...

    def complete_many(self, identifiers: tuple[int, ...]) -> Awaitable[int]:
        ...
