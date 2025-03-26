from collections.abc import Sequence
from typing import cast

from holobot.extensions.general.models import Badge
from holobot.extensions.general.models.items import BadgeDisplayInfo
from holobot.extensions.general.sdk.badges.exceptions import BadgeNotFoundException
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .ibadge_repository import IBadgeRepository
from .records import BadgeRecord

@injectable(IBadgeRepository)
class BadgeRepository(
    RepositoryBase[BadgeId, BadgeRecord, Badge],
    IBadgeRepository
):
    @property
    def record_type(self) -> type[BadgeRecord]:
        return BadgeRecord

    @property
    def model_type(self) -> type[Badge]:
        return Badge

    @property
    def identifier_type(self) -> type[BadgeId]:
        return BadgeId

    @property
    def table_name(self) -> str:
        return "badges"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def get_badge_name(self, badge_id: BadgeId) -> str | None:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, badge_id.server_id),
                    ("badge_id", Equality.EQUAL, badge_id.badge_id)
                )
            )
            result = await query.compile().fetchrow(session.connection)
            if result is None:
                return None

            return result.get("name", None)

    async def get_display_info(
        self,
        badge_id: BadgeId
    ) -> BadgeDisplayInfo:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("name", "emoji_id", "emoji_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, badge_id.server_id),
                    ("badge_id", Equality.EQUAL, badge_id.badge_id)
                )
            )
            if (result := await query.compile().fetchrow(session.connection)) is None:
                raise BadgeNotFoundException(badge_id)

            return BadgeDisplayInfo(
                badge_id=badge_id,
                name=cast(str, result.get("name")),
                emoji_id=cast(int, result.get("emoji_id")),
                emoji_name=cast(str, result.get("emoji_name"))
            )

    async def get_display_infos(
        self,
        server_id: int,
        badge_ids: Sequence[int]
    ) -> list[BadgeDisplayInfo]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("badge_id", "name", "emoji_id", "emoji_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .field_in("badge_id", badge_ids)
                .and_field("server_id", Equality.EQUAL, server_id)
            )
            records = await query.compile().fetch(session.connection)

            return [
                BadgeDisplayInfo(
                    badge_id=BadgeId(
                        server_id=server_id,
                        badge_id=cast(int, record.get("badge_id"))
                    ),
                    name=cast(str, record.get("name")),
                    emoji_id=cast(int, record.get("emoji_id")),
                    emoji_name=cast(str, record.get("emoji_name"))
                )
                for record in records
            ]

    async def paginate_badge_infos(
        self,
        server_id: int,
        name_part: str | None,
        page_index: int,
        page_size: int
    ) -> PaginationResult[BadgeDisplayInfo]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("badge_id", "name", "emoji_id", "emoji_name")
                .from_table(self.table_name, schema_name=self.schema_name)
                .where()
                .field("server_id", Equality.EQUAL, server_id)
            )

            if name_part:
                query = query.and_field("name", Equality.LIKE, name_part)

            result = await query.paginate(
                (("badge_id", Order.ASCENDING),),
                page_index,
                page_size
            ).compile().fetch(session.connection)

            return PaginationResult[BadgeDisplayInfo](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    BadgeDisplayInfo(
                        badge_id=BadgeId(
                            server_id=server_id,
                            badge_id=cast(int, record.get("badge_id"))
                        ),
                        name=cast(str, record.get("name")),
                        emoji_id=cast(int, record.get("emoji_id")),
                        emoji_name=cast(str, record.get("emoji_name"))
                    )
                    for record in result.records
                ]
            )

    def _map_record_to_model(self, record: BadgeRecord) -> Badge:
        return Badge(
            identifier=BadgeId(
                server_id=record.server_id.value,
                badge_id=record.badge_id.value
            ),
            created_by=record.created_by,
            created_at=record.created_at,
            name=record.name,
            description=record.description,
            emoji_name=record.emoji_name,
            emoji_id=record.emoji_id
        )

    def _map_model_to_record(self, model: Badge) -> BadgeRecord:
        return BadgeRecord(
            server_id=PrimaryKey(model.identifier.server_id),
            badge_id=PrimaryKey(model.identifier.badge_id),
            created_by=model.created_by,
            created_at=model.created_at,
            name=model.name,
            description=model.description,
            emoji_name=model.emoji_name,
            emoji_id=model.emoji_id
        )
