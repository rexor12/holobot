from datetime import timedelta

from hikari import ForbiddenError as HikariForbiddenError

from holobot.discord.bot import get_bot
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.servers.managers import (
    SILENCE_DURATION_MAX, SILENCE_DURATION_MIN, IUserManager
)
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range, textify_timedelta, utcnow

_DEFAULT_SILENCE_DURATION = timedelta(minutes=1)

@injectable(IUserManager)
class UserManager(IUserManager):
    async def silence_user(
        self,
        server_id: str,
        user_id: str,
        duration: timedelta | None = None
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        if not duration:
            duration = _DEFAULT_SILENCE_DURATION
        if duration > SILENCE_DURATION_MAX or duration < SILENCE_DURATION_MIN:
            raise ArgumentOutOfRangeError(
                "duration",
                textify_timedelta(SILENCE_DURATION_MIN),
                textify_timedelta(SILENCE_DURATION_MAX)
            )

        member = await get_bot().get_guild_member(int(server_id), int(user_id))
        try:
            await member.edit(communication_disabled_until=utcnow() + duration)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot time-out server member.") from error

    async def kick_user(self, server_id: str, user_id: str, reason: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")

        member = await get_bot().get_guild_member(int(server_id), int(user_id))
        try:
            await member.kick(reason=reason)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot kick server member.") from error

    async def ban_user(self, server_id: str, user_id: str, reason: str, delete_message_days: int = 0) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")
        assert_range(delete_message_days, 0, 7, "delete_message_days")

        member = await get_bot().get_guild_member(int(server_id), int(user_id))
        try:
            await member.ban(reason=reason, delete_message_days=delete_message_days)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot ban server member.") from error

    async def assign_role(self, server_id: str, user_id: str, role_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(role_id, "role_id")

        member = await get_bot().get_guild_member(int(server_id), int(user_id))
        role = await get_bot().get_guild_role(int(server_id), int(role_id))
        try:
            await member.add_role(role)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot assign role to server member.") from error

    async def remove_role(self, server_id: str, user_id: str, role_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(role_id, "role_id")

        member = await get_bot().get_guild_member(int(server_id), int(user_id))
        role = await get_bot().get_guild_role(int(server_id), int(role_id))
        try:
            await member.remove_role(role)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot remove role from server member.") from error

    async def unsilence_user(
        self,
        server_id: str,
        user_id: str
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        member = await get_bot().get_guild_member(int(server_id), int(user_id))
        try:
            await member.edit(communication_disabled_until=None)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot remove time-out of server member.") from error
