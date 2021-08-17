from .iwarn_manager import IWarnManager
from .. import IConfigProvider
from ..models import WarnStrike
from ..repositories import IWarnRepository, IWarnSettingsRepository
from datetime import timedelta
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import Optional, Tuple

@injectable(IWarnManager)
class WarnManager(IWarnManager):
    def __init__(self,
        config_provider: IConfigProvider,
        warn_repository: IWarnRepository,
        warn_settings_repository: IWarnSettingsRepository) -> None:
        super().__init__()
        self.__config_provider: IConfigProvider = config_provider
        self.__warn_repository: IWarnRepository = warn_repository
        self.__warn_settings_repository: IWarnSettingsRepository = warn_settings_repository

    async def get_warns(self, server_id: str, user_id: str, page_index: int, page_size: int) -> Tuple[WarnStrike, ...]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if page_index < 0:
            page_index = 0
        if page_size < 0:
            return ()
        return await self.__warn_repository.get_warns_by_user(server_id, user_id, page_index * page_size, page_size)
    
    async def warn_user(self, server_id: str, user_id: str, reason: str, warner_id: str) -> WarnStrike:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")
        assert_not_none(warner_id, "warner_id")

        decay_threshold = await self.__warn_settings_repository.get_warn_decay_threshold(server_id)
        warn_strike = WarnStrike()
        warn_strike.server_id = server_id
        warn_strike.user_id = user_id
        warn_strike.reason = reason
        warn_strike.warner_id = warner_id
        warn_strike.id = await self.__warn_repository.add_warn(warn_strike, decay_threshold)
        return warn_strike
    
    async def clear_warns_for_user(self, server_id: str, user_id: str) -> int:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        return await self.__warn_repository.clear_warns_by_user(server_id, user_id)
    
    async def clear_warns_for_server(self, server_id: str) -> int:
        assert_not_none(server_id, "server_id")

        return await self.__warn_repository.clear_warns_by_server(server_id)
    
    async def enable_auto_mute(self, server_id: str, warn_count: int, duration: Optional[timedelta]) -> None:
        assert_not_none(server_id, "server_id")

        if duration is not None:
            duration_range = self.__config_provider.get_mute_duration_range()
            if not duration in duration_range:
                raise ArgumentOutOfRangeError(
                    "duration",
                    str(duration_range.lower_bound),
                    str(duration_range.upper_bound)
                )
        await self.__warn_settings_repository.set_auto_mute(server_id, warn_count, duration)
    
    async def disable_auto_mute(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        await self.__warn_settings_repository.set_auto_mute(server_id, None, None)
    
    async def enable_auto_kick(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")

        await self.__warn_settings_repository.set_auto_kick(server_id, warn_count)
    
    async def disable_auto_kick(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        await self.__warn_settings_repository.set_auto_kick(server_id, None)
    
    async def enable_auto_ban(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")

        await self.__warn_settings_repository.set_auto_ban(server_id, warn_count)
    
    async def disable_auto_ban(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        await self.__warn_settings_repository.set_auto_ban(server_id, None)
    
    async def set_warn_decay(self, server_id: str, decay_time: Optional[timedelta]) -> None:
        assert_not_none(server_id, "server_id")

        if decay_time is None:
            await self.__warn_settings_repository.clear_warn_decay_threshold(server_id)
            return
        
        decay_range = self.__config_provider.get_decay_threshold_range()
        if not decay_time in decay_range:
            raise ArgumentOutOfRangeError(
                "decay_time",
                str(decay_range.lower_bound),
                str(decay_range.upper_bound)
            )

        await self.__warn_settings_repository.set_warn_decay_threshold(server_id, decay_time)
