from .utils import get_guild_member
from discord.errors import Forbidden
from holobot.discord.sdk import IUserManager
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.sdk.ioc.decorators import injectable

@injectable(IUserManager)
class UserManager(IUserManager):
    async def kick_user(self, server_id: str, user_id: str, reason: str) -> None:
        member = get_guild_member(server_id, user_id)
        try:
            await member.kick(reason=reason)
        except Forbidden:
            raise ForbiddenError()

    async def ban_user(self, server_id: str, user_id: str, reason: str, delete_message_days: int = 0) -> None:
        member = get_guild_member(server_id, user_id)
        try:
            await member.ban(reason=reason, delete_message_days=delete_message_days)
        except Forbidden:
            raise ForbiddenError()
