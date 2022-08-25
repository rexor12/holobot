from datetime import datetime, timezone

from holobot.discord.sdk import IMessaging
from holobot.extensions.moderation.models import LogSettings
from holobot.extensions.moderation.repositories import ILogSettingsRepository
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import assert_not_none
from .ilog_manager import ILogManager

@injectable(ILogManager)
class LogManager(ILogManager):
    def __init__(self,
        log_settings_repository: ILogSettingsRepository,
        logger_factory: ILoggerFactory,
        messaging: IMessaging
    ) -> None:
        super().__init__()
        self.__log = logger_factory.create(LogManager)
        self.__log_settings_repository: ILogSettingsRepository = log_settings_repository
        self.__messaging: IMessaging = messaging

    async def set_log_channel(self, server_id: str, channel_id: str | None) -> None:
        assert_not_none(server_id, "server_id")

        if not channel_id:
            await self.__log_settings_repository.delete_by_server(server_id)
            return

        log_settings = await self.__log_settings_repository.get_by_server(server_id)
        if not log_settings:
            await self.__log_settings_repository.add(LogSettings(
                server_id=server_id,
                channel_id=channel_id
            ))
            return

        log_settings.modified_at = datetime.now(timezone.utc)
        log_settings.channel_id = channel_id
        await self.__log_settings_repository.update(log_settings)

    async def publish_log_entry(self, server_id: str, message: str) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(message, "message")

        log_settings = await self.__log_settings_repository.get_by_server(server_id)
        if not log_settings or not log_settings.channel_id:
            return False

        await self.__messaging.send_channel_message(server_id, log_settings.channel_id, message)
        return True
