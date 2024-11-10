from collections.abc import Awaitable, Callable

from holobot.extensions.mudada.models import Transaction
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import WhereBuilder, WhereConstraintBuilder
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .itransaction_repository import ITransactionRepository
from .records import TransactionRecord

@injectable(ITransactionRepository)
class TransactionRepository(
    RepositoryBase[int, TransactionRecord, Transaction],
    ITransactionRepository
):
    @property
    def record_type(self) -> type[TransactionRecord]:
        return TransactionRecord

    @property
    def model_type(self) -> type[Transaction]:
        return Transaction

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "mudada_transactions"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def get_by_users(self, owner_id: int, target_id: int) -> Awaitable[Transaction | None]:
        return self._get_by_filter(lambda where: where.fields(
            Connector.AND,
            ("owner_id", Equality.EQUAL, owner_id),
            ("target_id", Equality.EQUAL, target_id)
        ))

    async def get_total_transaction_amount(
        self,
        owner_id: int,
        include_finalized: bool
    ) -> int:
        async with (session := await self._get_session()):
            query_string = (
                f"SELECT SUM(amount) FROM {self.table_name} WHERE owner_id = $1"
                if include_finalized
                else f"SELECT SUM(amount) FROM {self.table_name} WHERE owner_id = $1 AND is_finalized = false"
            )
            result: int | None = await session.connection.fetchval(query_string, owner_id)

            return result or 0

    def delete_all_by_user(self, owner_id: int, delete_finalized: bool) -> Awaitable[int]:
        filter: Callable[[WhereBuilder], WhereConstraintBuilder] = (
            (lambda where: where.field("owner_id", Equality.EQUAL, owner_id))
            if delete_finalized
            else (lambda where: where.fields(
                Connector.AND,
                ("owner_id", Equality.EQUAL, owner_id),
                ("is_finalized", Equality.EQUAL, False)
            ))
        )

        return self._delete_by_filter(filter)

    def paginate_by_owner(
        self,
        owner_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[Transaction]]:
        return self._paginate(
            (("id", Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.field("owner_id", Equality.EQUAL, owner_id)
        )

    def paginate_by_target(
        self,
        target_id: int,
        page_index: int,
        page_size: int,
        finalized_only: bool
    ) -> Awaitable[PaginationResult[Transaction]]:
        return self._paginate(
            (("id", Order.ASCENDING),),
            page_index,
            page_size,
            (
                (lambda where: where.fields(
                    Connector.AND,
                    ("target_id", Equality.EQUAL, target_id),
                    ("is_finalized", Equality.EQUAL, True),
                    ("is_completed", Equality.EQUAL, False)
                ))
                if finalized_only
                else (lambda where: where.fields(
                    Connector.AND,
                    ("target_id", Equality.EQUAL, target_id),
                    ("is_completed", Equality.EQUAL, False)
                ))
            )
        )

    def get_finalized_uncompleted_by_target(
        self,
        target_id: int
    ) -> Awaitable[tuple[Transaction, ...]]:
        return self._get_many_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("is_finalized", Equality.EQUAL, True),
                ("is_completed", Equality.EQUAL, False),
                ("target_id", Equality.EQUAL, target_id)
            )
        )

    def complete_many(self, identifiers: tuple[int, ...]) -> Awaitable[int]:
        return self._update_by_filter(
            (("is_completed", True, False),),
            lambda where: where.field_in("id", identifiers)
        )

    def _map_record_to_model(self, record: TransactionRecord) -> Transaction:
        return Transaction(
            identifier=record.id.value,
            created_at=record.created_at,
            owner_id=record.owner_id,
            target_id=record.target_id,
            amount=record.amount,
            message=record.message,
            is_finalized=record.is_finalized,
            is_completed=record.is_completed
        )

    def _map_model_to_record(self, model: Transaction) -> TransactionRecord:
        return TransactionRecord(
            id=PrimaryKey(model.identifier),
            created_at=model.created_at,
            owner_id=model.owner_id,
            target_id=model.target_id,
            amount=model.amount,
            message=model.message,
            is_finalized=model.is_finalized,
            is_completed=model.is_completed
        )
