from .ilog_manager import ILogManager
from ..repositories import ILogSettingsRepository
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import Optional

@injectable(ILogManager)
class LogManager(ILogManager):
    def __init__(self, log_settings_repository: ILogSettingsRepository) -> None:
        super().__init__()
        self.__log_settings_repository: ILogSettingsRepository = log_settings_repository

    async def set_log_channel(self, server_id: str, channel_id: Optional[str]) -> None:
        assert_not_none(server_id, "server_id")

        if not channel_id:
            await self.__log_settings_repository.clear_log_channel(server_id)
            return
        
        await self.__log_settings_repository.set_log_channel(server_id, channel_id)
