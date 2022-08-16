from .ilog_manager import ILogManager
from ..repositories import ILogSettingsRepository
from holobot.discord.sdk import IMessaging
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import assert_not_none

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
            await self.__log_settings_repository.clear_log_channel(server_id)
            return

        await self.__log_settings_repository.set_log_channel(server_id, channel_id)

    async def publish_log_entry(self, server_id: str, message: str) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(message, "message")

        channel_id = await self.__log_settings_repository.get_log_channel(server_id)
        if not channel_id:
            return False

        await self.__messaging.send_channel_message(server_id, channel_id, message)
        return True
