from .imute_manager import IMuteManager
from .. import IConfigProvider
from ..constants import MUTED_ROLE_NAME
from ..exceptions import RoleNotFoundError
from ..repositories import IMutesRepository
from datetime import datetime, timedelta
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.servers.managers import IChannelManager, IRoleManager, IUserManager
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, textify_timedelta
from typing import List, Optional

@injectable(IMuteManager)
class MuteManager(IMuteManager):
    def __init__(self,
        channel_manager: IChannelManager,
        config_provider: IConfigProvider,
        mutes_repository: IMutesRepository,
        role_manager: IRoleManager,
        user_manager: IUserManager) -> None:
        super().__init__()
        self.__channel_manager: IChannelManager = channel_manager
        self.__config_provider: IConfigProvider = config_provider
        self.__mutes_repository: IMutesRepository = mutes_repository
        self.__role_manager: IRoleManager = role_manager
        self.__user_manager: IUserManager = user_manager

    async def mute_user(self, server_id: str, user_id: str, reason: str, duration: Optional[timedelta] = None) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")

        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            raise ArgumentOutOfRangeError("reason", str(reason_length_range.lower_bound), str(reason_length_range.upper_bound))

        if duration is not None:
            duration_range = self.__config_provider.get_mute_duration_range()
            if duration < duration_range.lower_bound or duration > duration_range.upper_bound:
                raise ArgumentOutOfRangeError(
                    "duration",
                    textify_timedelta(duration_range.lower_bound),
                    textify_timedelta(duration_range.upper_bound)
                )

        if not (muted_role := self.__role_manager.get_role(server_id, MUTED_ROLE_NAME)):
            muted_role = await self.__role_manager.create_role(server_id, MUTED_ROLE_NAME, "Used for muting people in text channels.")
            for channel in self.__channel_manager.get_channels(server_id):
                await self.__channel_manager.set_role_permissions(server_id, channel.id, muted_role.id, (Permission.SEND_MESSAGES, False))

        await self.__user_manager.assign_role(server_id, user_id, muted_role.id)

        if duration is not None:
            await self.__mutes_repository.upsert_mute(server_id, user_id, datetime.utcnow() + duration)

    async def unmute_user(self, server_id: str, user_id: str, clear_auto_unmute: bool = True) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if not (muted_role := self.__role_manager.get_role(server_id, MUTED_ROLE_NAME)):
            raise RoleNotFoundError(MUTED_ROLE_NAME)

        await self.__user_manager.remove_role(server_id, user_id, muted_role.id)
        
        if clear_auto_unmute:
            await self.__mutes_repository.delete_mute(server_id, user_id)
