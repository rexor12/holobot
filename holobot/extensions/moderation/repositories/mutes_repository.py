from datetime import datetime

from asyncpg.connection import Connection

from holobot.extensions.moderation.models import Mute
from holobot.sdk.database import IDatabaseManager
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from .imutes_repository import IMutesRepository
from .records import MuteRecord

@injectable(IMutesRepository)
class MutesRepository(
    RepositoryBase[int, MuteRecord, Mute],
    IMutesRepository
):
    @property
    def record_type(self) -> type[MuteRecord]:
        return MuteRecord

    @property
    def table_name(self) -> str:
        return "moderation_mutes"

    def __init__(self, database_manager: IDatabaseManager) -> None:
        super().__init__(database_manager)

    async def upsert_mute(self, server_id: str, user_id: str, expires_at: datetime) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(self.table_name).fields(
                    ("server_id", server_id),
                    ("user_id", user_id),
                    ("expires_at", expires_at)
                ).on_conflict("server_id", "user_id").update().field(
                    "expires_at", expires_at
                ).field(
                    "modified_at", "(NOW() AT TIME ZONE 'utc')", True
                ).compile().execute(connection)

    async def delete_mute(self, server_id: str, user_id: str) -> int:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                status: CommandComplete[DeleteCommandTag] = await Query.delete().from_table(self.table_name).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, server_id),
                    ("user_id", Equality.EQUAL, user_id)
                ).compile().execute(connection)

                return status.command_tag.rows

    async def delete_expired_mutes(self) -> tuple[Mute, ...]:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await Query.delete().from_table(self.table_name).where().field(
                    "expires_at", Equality.LESS, "(NOW() at time zone 'utc')", True
                ).returning().columns(
                    "id", "server_id", "user_id"
                ).compile().fetch(connection)

                return tuple(
                    self._map_record_to_model(self._map_query_result_to_record(record))
                    for record in records
                )

    def _map_record_to_model(self, record: MuteRecord) -> Mute:
        return Mute(
            identifier=record.id,
            server_id=record.server_id,
            user_id=record.user_id
        )

    def _map_model_to_record(self, model: Mute) -> MuteRecord:
        return MuteRecord(
            id=model.identifier,
            server_id=model.server_id,
            user_id=model.user_id
        )
