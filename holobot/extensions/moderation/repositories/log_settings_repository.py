from collections.abc import Awaitable

from holobot.extensions.moderation.models import LogSettings
from holobot.extensions.moderation.repositories.records import LogSettingsRecord
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
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
    def model_type(self) -> type[LogSettings]:
        return LogSettings

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "moderation_log_settings"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def get_by_server(self, server_id: str) -> Awaitable[LogSettings | None]:
        assert_not_none(server_id, "server_id")

        return self._get_by_filter(lambda where: (
            where.field("server_id", Equality.EQUAL, server_id)
        ))

    def delete_by_server(self, server_id: str) -> Awaitable[int]:
        assert_not_none(server_id, "server_id")

        return self._delete_by_filter(
            lambda where: where.field("server_id", Equality.EQUAL, server_id)
        )

    def _map_record_to_model(self, record: LogSettingsRecord) -> LogSettings:
        return LogSettings(
            identifier=record.id.value,
            modified_at=record.modified_at,
            server_id=record.server_id,
            channel_id=record.channel_id
        )

    def _map_model_to_record(self, model: LogSettings) -> LogSettingsRecord:
        return LogSettingsRecord(
            id=PrimaryKey(model.identifier),
            modified_at=model.modified_at,
            server_id=model.server_id,
            channel_id=model.channel_id
        )
