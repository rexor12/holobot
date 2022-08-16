from hikari import ForbiddenError as HikariForbiddenError

from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.discord.utils import get_guild_member, get_guild_role
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none, assert_range

@injectable(IUserManager)
class UserManager(IUserManager):
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
