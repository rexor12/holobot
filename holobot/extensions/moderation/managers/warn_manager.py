from .iwarn_manager import IWarnManager
from ..models import WarnStrike
from ..repositories import IWarnRepository
from datetime import timedelta
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from typing import Tuple

@injectable(IWarnManager)
class WarnManager(IWarnManager):
    def __init__(self, repository: IWarnRepository) -> None:
        super().__init__()
        self.__repository: IWarnRepository = repository

    async def get_warns(self, server_id: str, user_id: str, page_index: int, page_size: int) -> Tuple[WarnStrike, ...]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        if page_index < 0:
            page_index = 0
        if page_size < 0:
            return ()
        return await self.__repository.get_warns_by_user(server_id, user_id, page_index * page_size, page_size)
    
    async def warn_user(self, server_id: str, user_id: str, reason: str, warner_id: str) -> WarnStrike:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")
        assert_not_none(warner_id, "warner_id")
        warn_strike = WarnStrike()
        warn_strike.server_id = server_id
        warn_strike.user_id = user_id
        warn_strike.reason = reason
        warn_strike.warner_id = warner_id
        warn_strike.id = await self.__repository.add_warn(warn_strike)
        return warn_strike
    
    async def clear_warns_for_user(self, server_id: str, user_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        await self.__repository.clear_warns_by_user(server_id, user_id)
    
    async def clear_warns_for_server(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")
        await self.__repository.clear_warns_by_server(server_id)
    
    async def enable_auto_mute(self, server_id: str, warn_count: int, duration: timedelta) -> None:
        assert_not_none(server_id, "server_id")
        raise NotImplementedError
    
    async def disable_auto_mute(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")
        raise NotImplementedError
    
    async def enable_auto_kick(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")
        raise NotImplementedError
    
    async def disable_auto_kick(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")
        raise NotImplementedError
    
    async def enable_auto_ban(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")
        raise NotImplementedError
    
    async def disable_auto_ban(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")
        raise NotImplementedError
    
    async def set_warn_decay(self, server_id: str, decay_time: timedelta) -> None:
        assert_not_none(server_id, "server_id")
        raise NotImplementedError
