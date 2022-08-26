from datetime import datetime, timedelta, timezone

from hikari import ForbiddenError as HikariForbiddenError

from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.discord.utils import get_guild_member, get_guild_role
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range, textify_timedelta

_DEFAULT_TIME_OUT_DURATION = timedelta(minutes=1)
_MIN_TIME_OUT = timedelta(minutes=1)
_MAX_TIME_OUT = timedelta(days=27)

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
            duration = _DEFAULT_TIME_OUT_DURATION
        if duration > _MAX_TIME_OUT or duration < _MIN_TIME_OUT:
            raise ArgumentError(
                "duration",
                (
                    f"The duration must be between {textify_timedelta(_MIN_TIME_OUT)}"
                    f" and {textify_timedelta(_MAX_TIME_OUT)}."
                )
            )

        member = get_guild_member(server_id, user_id)
        try:
            await member.edit(communication_disabled_until=datetime.now(timezone.utc) + duration)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot time-out server member.") from error

    async def kick_user(self, server_id: str, user_id: str, reason: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")

        member = get_guild_member(server_id, user_id)
        try:
            await member.kick(reason=reason)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot kick server member.") from error

    async def ban_user(self, server_id: str, user_id: str, reason: str, delete_message_days: int = 0) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")
        assert_range(delete_message_days, 0, 7, "delete_message_days")

        member = get_guild_member(server_id, user_id)
        try:
            await member.ban(reason=reason, delete_message_days=delete_message_days)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot ban server member.") from error

    async def assign_role(self, server_id: str, user_id: str, role_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(role_id, "role_id")

        member = get_guild_member(server_id, user_id)
        role = get_guild_role(server_id, role_id)
        try:
            await member.add_role(role)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot assign role to server member.") from error

    async def remove_role(self, server_id: str, user_id: str, role_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(role_id, "role_id")

        member = get_guild_member(server_id, user_id)
        role = get_guild_role(server_id, role_id)
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

        member = get_guild_member(server_id, user_id)
        try:
            await member.edit(communication_disabled_until=None)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot remove time-out of server member.") from error
