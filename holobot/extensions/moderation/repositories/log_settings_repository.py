from asyncpg.connection import Connection

from holobot.extensions.moderation.models import LogSettings
from holobot.extensions.moderation.repositories.records import LogSettingsRecord
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from .ilog_settings_repository import ILogSettingsRepository

@injectable(ILogSettingsRepository)
class LogSettingsRepository(
    RepositoryBase[int, LogSettingsRecord, LogSettings],
    ILogSettingsRepository
):
    @property
    def record_type(self) -> type[LogSettingsRecord]:
        return LogSettingsRecord

    @property
    def table_name(self) -> str:
        return "moderation_log_settings"

    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__(database_manager)

    async def get_by_server(self, server_id: str) -> LogSettings | None:
        assert_not_none(server_id, "server_id")

        return await self._get_one_by_filter(lambda where: (
            where.field("server_id", Equality.EQUAL, server_id)
        ))

    async def delete_by_server(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(self.table_name).where().field(
                    "server_id", Equality.EQUAL, server_id
                ).compile().execute(connection)

    def _map_record_to_model(self, record: LogSettingsRecord) -> LogSettings:
        return LogSettings(
            identifier=record.id,
            modified_at=record.modified_at,
            server_id=record.server_id,
            channel_id=record.channel_id
        )

    def _map_model_to_record(self, model: LogSettings) -> LogSettingsRecord:
        return LogSettingsRecord(
            id=model.identifier,
            modified_at=model.modified_at,
            server_id=model.server_id,
            channel_id=model.channel_id
        )
