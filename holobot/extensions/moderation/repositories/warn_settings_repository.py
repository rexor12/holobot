from holobot.extensions.moderation.models import WarnSettings
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from .iwarn_settings_repository import IWarnSettingsRepository
from .records import WarnSettingsRecord

@injectable(IWarnSettingsRepository)
class WarnSettingsRepository(
    RepositoryBase[int, WarnSettingsRecord, WarnSettings],
    IWarnSettingsRepository
):
    @property
    def record_type(self) -> type[WarnSettingsRecord]:
        return WarnSettingsRecord

    @property
    def model_type(self) -> type[WarnSettings]:
        return WarnSettings

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "moderation_warn_settings"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def get_by_server(self, server_id: int) -> WarnSettings | None:
        assert_not_none(server_id, "server_id")

        return await self._get_by_filter(lambda where: (
            where.field("server_id", Equality.EQUAL, server_id)
        ))

    def _map_record_to_model(self, record: WarnSettingsRecord) -> WarnSettings:
        return WarnSettings(
            identifier=record.id.value,
            modified_at=record.modified_at,
            server_id=record.server_id,
            decay_threshold=record.decay_threshold,
            auto_mute_after=record.auto_mute_after,
            auto_mute_duration=record.auto_mute_duration,
            auto_kick_after=record.auto_kick_after,
            auto_ban_after=record.auto_ban_after
        )

    def _map_model_to_record(self, model: WarnSettings) -> WarnSettingsRecord:
        return WarnSettingsRecord(
            id=PrimaryKey(model.identifier),
            modified_at=model.modified_at,
            server_id=model.server_id,
            decay_threshold=model.decay_threshold,
            auto_mute_after=model.auto_mute_after,
            auto_mute_duration=model.auto_mute_duration,
            auto_kick_after=model.auto_kick_after,
            auto_ban_after=model.auto_ban_after
        )
