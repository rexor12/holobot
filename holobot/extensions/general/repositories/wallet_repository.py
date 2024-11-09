from collections.abc import Awaitable

from holobot.extensions.general.models import Wallet, WalletWithDetailsDto
from holobot.extensions.general.sdk.wallets.models import WalletId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import WhereBuilder, WhereConstraintBuilder
from holobot.sdk.database.queries.constraints import column_expression, or_expression
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.database.queries.enums.order import Order
from holobot.sdk.database.queries.query import Query
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .iwallet_repository import IWalletRepository
from .records import WalletRecord

@injectable(IWalletRepository)
class WalletRepository(
    RepositoryBase[WalletId, WalletRecord, Wallet],
    IWalletRepository
):
    @property
    def record_type(self) -> type[WalletRecord]:
        return WalletRecord

    @property
    def model_type(self) -> type[Wallet]:
        return Wallet

    @property
    def identifier_type(self) -> type[WalletId]:
        return WalletId

    @property
    def table_name(self) -> str:
        return "wallets"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def get_wallets(
        self,
        user_id: int,
        server_id: int | None = None,
        include_global: bool = False
    ) -> Awaitable[tuple[Wallet, ...]]:
        return self._get_many_by_filter(lambda where: WalletRepository.__build_wallet_constraint(
            where,
            user_id,
            server_id,
            include_global
        ))

    async def paginate_wallets_with_details(
        self,
        user_id: int,
        server_id: int | None = None,
        include_global: bool = False,
        page_index: int = 0,
        page_size: int = 5
    ) -> PaginationResult[WalletWithDetailsDto]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns(
                    "wallets.user_id", "wallets.currency_id", "wallets.server_id", "wallets.amount",
                    "currencies.name", "currencies.emoji_id", "currencies.emoji_name"
                )
                .from_table("wallets")
                .join("currencies", "currency_id", "id", join_type="INNER")
            )
            query = WalletRepository.__build_wallet_constraint(
                query.where(),
                user_id,
                server_id,
                include_global
            )
            result = await query.paginate(
                (("server_id", Order.ASCENDING),),
                page_index,
                page_size
            ).compile().fetch(session.connection)

            return PaginationResult(
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    WalletWithDetailsDto(
                        wallet_id=WalletId(
                            user_id=record.get("user_id", ""),
                            currency_id=int(record.get("currency_id", "0")),
                            server_id=record.get("server_id", "")
                        ),
                        amount=int(record.get("amount", "0")),
                        currency_name=record.get("name", ""),
                        currency_emoji_id=int(record.get("emoji_id", "0")),
                        currency_emoji_name=record.get("emoji_name", "")
                    )
                    for record in result.records
                ]
            )

    async def remove_from_all_users(self, amount: int) -> None:
        async with (session := await self._get_session()):
            await session.connection.execute(
                f"UPDATE {self.table_name} SET amount = CASE WHEN amount >= $1 THEN amount - $1 ELSE 0 END",
                amount
            )

    def _map_record_to_model(self, record: WalletRecord) -> Wallet:
        return Wallet(
            identifier=WalletId(
                user_id=record.user_id.value,
                currency_id=record.currency_id.value,
                server_id=record.server_id.value
            ),
            amount=record.amount
        )

    def _map_model_to_record(self, model: Wallet) -> WalletRecord:
        return WalletRecord(
            user_id=PrimaryKey(model.identifier.user_id),
            currency_id=PrimaryKey(model.identifier.currency_id),
            server_id=PrimaryKey(model.identifier.server_id),
            amount=model.amount
        )

    @staticmethod
    def __build_wallet_constraint(
        where: WhereBuilder,
        user_id: int,
        server_id: int | None,
        include_global: bool
    ) -> WhereConstraintBuilder:
        constraint = (where
            .field("wallets.user_id", Equality.EQUAL, user_id)
            .and_field("wallets.amount", Equality.GREATER, 0)
        )
        if server_id is None:
            return constraint

        if include_global:
            constraint = constraint.and_expression(
                or_expression(
                    column_expression("wallets.server_id", Equality.EQUAL, server_id),
                    column_expression("wallets.server_id", Equality.EQUAL, 0)
                )
            )
        else:
            constraint = constraint.and_field("wallets.server_id", Equality.EQUAL, server_id)

        return constraint
