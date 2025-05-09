from collections.abc import Awaitable, Iterable, Sequence
from typing import cast

from holobot.extensions.general.models import Currency
from holobot.extensions.general.models.items import CurrencyDisplayInfo
from holobot.extensions.general.sdk.currencies.data_providers import ICurrencyDataProvider
from holobot.extensions.general.sdk.currencies.exceptions import CurrencyNotFoundException
from holobot.extensions.general.sdk.currencies.models import ICurrency
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries.constraints import (
    and_expression, column_expression, column_like_expression
)
from holobot.sdk.database.queries.constraints.logical_constraint_builder import or_expression
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.queries.query import Query
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .icurrency_repository import ICurrencyRepository
from .records import CurrencyRecord

@injectable(ICurrencyRepository)
@injectable(ICurrencyDataProvider)
class CurrencyRepository(
    RepositoryBase[int, CurrencyRecord, Currency],
    ICurrencyRepository
):
    @property
    def record_type(self) -> type[CurrencyRecord]:
        return CurrencyRecord

    @property
    def model_type(self) -> type[Currency]:
        return Currency

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "currencies"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def paginate_by_server(
        self,
        server_id: int,
        page_index: int,
        page_size: int,
        include_global: bool
    ) -> Awaitable[PaginationResult[Currency]]:
        def build_server_filter():
            if include_global:
                return or_expression(
                    column_expression("server_id", Equality.EQUAL, server_id),
                    column_expression("server_id", Equality.EQUAL, None)
                )
            return column_expression("server_id", Equality.EQUAL, server_id)

        return self._paginate(
            (("id", Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.field("server_id", Equality.EQUAL, server_id)
        )

    def count_by_server(self, server_id: int) -> Awaitable[int]:
        return self._count_by_filter(lambda where: where.field("server_id", Equality.EQUAL, server_id))

    def delete_by_server(self, currency_id: int, server_id: int) -> Awaitable[int]:
        return self._delete_by_filter(lambda where: where.fields(
            Connector.AND,
            ("id", Equality.EQUAL, currency_id),
            ("server_id", Equality.EQUAL, server_id)
        ))

    def try_get_by_server(
        self,
        currency_id: int,
        server_id: int,
        allow_global: bool
    ) -> Awaitable[Currency | None]:
        def build_filter():
            id_constraint = column_expression("id", Equality.EQUAL, currency_id)
            if allow_global:
                return and_expression(
                    id_constraint,
                    or_expression(
                        column_expression("server_id", Equality.EQUAL, server_id),
                        column_expression("server_id", Equality.EQUAL, None)
                    )
                )
            return and_expression(
                id_constraint,
                column_expression("server_id", Equality.EQUAL, server_id)
            )

        return self._get_by_filter(lambda where: where.expression(build_filter()))

    async def search(
        self,
        text: str,
        server_id: int,
        max_count: int,
        include_global: bool
    ) -> Iterable[tuple[int, str]]:
        def build_filter():
            name_constraint = column_like_expression("name", text, True)
            if include_global:
                return and_expression(
                    name_constraint,
                    or_expression(
                        column_expression("server_id", Equality.EQUAL, server_id),
                        column_expression("server_id", Equality.EQUAL, None)
                    )
                )
            return and_expression(
                name_constraint,
                column_expression("server_id", Equality.EQUAL, server_id)
            )

        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("id", "name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .expression(build_filter())
                .limit()
                .max_count(max_count)
            )
            results = await query.compile().fetch(session.connection)

            return tuple(
                (
                    int(result.get("id", "0")),
                    result.get("name", "")
                )
                for result in results
            )

    async def get_display_info(
        self,
        currency_id: int
    ) -> CurrencyDisplayInfo:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("id", "name", "emoji_id", "emoji_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .field("id", Equality.EQUAL, currency_id)
            )
            if (result := await query.compile().fetchrow(session.connection)) is None:
                raise CurrencyNotFoundException(currency_id)

            return CurrencyDisplayInfo(
                currency_id=cast(int, result.get("id")),
                name=cast(str, result.get("name")),
                emoji_id=cast(int, result.get("emoji_id")),
                emoji_name=cast(str, result.get("emoji_name"))
            )

    async def get_display_infos(
        self,
        currency_ids: Sequence[int]
    ) -> list[CurrencyDisplayInfo]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("id", "name", "emoji_id", "emoji_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .field_in("id", currency_ids)
            )
            records = await query.compile().fetch(session.connection)

            return [
                CurrencyDisplayInfo(
                    currency_id=cast(int, record.get("id")),
                    name=cast(str, record.get("name")),
                    emoji_id=cast(int, record.get("emoji_id")),
                    emoji_name=cast(str, record.get("emoji_name"))
                )
                for record in records
            ]

    def get_currency_by_code(self, server_id: int, code: str) -> Awaitable[ICurrency | None]:
        return self._get_by_filter(lambda where: where.fields(
            Connector.AND,
            ("server_id", Equality.EQUAL, server_id),
            ("code", Equality.EQUAL, code)
        ))

    async def paginate_currency_infos(
        self,
        server_id: int,
        name_part: str | None,
        page_index: int,
        page_size: int
    ) -> PaginationResult[CurrencyDisplayInfo]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("id", "name", "emoji_id", "emoji_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .field("server_id", Equality.EQUAL, server_id)
            )

            if name_part:
                query = query.and_field("name", Equality.LIKE, name_part)

            result = await query.paginate(
                (("id", Order.ASCENDING),),
                page_index,
                page_size
            ).compile().fetch(session.connection)

            return PaginationResult[CurrencyDisplayInfo](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    CurrencyDisplayInfo(
                        currency_id=cast(int, record.get("id")),
                        name=cast(str, record.get("name")),
                        emoji_id=cast(int, record.get("emoji_id")),
                        emoji_name=cast(str, record.get("emoji_name"))
                    )
                    for record in result.records
                ]
            )

    def _map_record_to_model(self, record: CurrencyRecord) -> Currency:
        return Currency(
            identifier=record.id.value,
            created_at=record.created_at,
            created_by=record.created_by,
            server_id=record.server_id,
            name=record.name,
            description=record.description,
            emoji_id=record.emoji_id,
            emoji_name=record.emoji_name,
            is_tradable=record.is_tradable
        )

    def _map_model_to_record(self, model: Currency) -> CurrencyRecord:
        return CurrencyRecord(
            id=PrimaryKey(model.identifier),
            created_at=model.created_at,
            created_by=model.created_by,
            server_id=model.server_id,
            name=model.name,
            description=model.description,
            emoji_id=model.emoji_id,
            emoji_name=model.emoji_name,
            is_tradable=model.is_tradable
        )
