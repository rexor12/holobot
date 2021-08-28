from .ilog_manager import ILogManager
from ..repositories import ILogSettingsRepository
from holobot.discord.sdk import IMessaging
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import assert_not_none
from typing import Optional

@injectable(ILogManager)
class LogManager(ILogManager):
    def __init__(self,
        log: LogInterface,
        log_settings_repository: ILogSettingsRepository,
        messaging: IMessaging) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "LogManager")
        self.__log_settings_repository: ILogSettingsRepository = log_settings_repository
        self.__messaging: IMessaging = messaging

    async def set_log_channel(self, server_id: str, channel_id: Optional[str]) -> None:
        assert_not_none(server_id, "server_id")

        if not channel_id:
            await self.__log_settings_repository.clear_log_channel(server_id)
            return
        
        await self.__log_settings_repository.set_log_channel(server_id, channel_id)
    
    async def publish_log_entry(self, server_id: str, message: str) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(message, "message")

        log_channel = await self.__log_settings_repository.get_log_channel(server_id)
        if not log_channel:
            return False

        await self.__messaging.send_channel_message(log_channel, message)
        return True
