from .bot import Bot
from discord.errors import Forbidden
from discord.guild import Guild, Member
from holobot.discord.sdk import IUserManager
from holobot.discord.sdk.exceptions import ForbiddenError, ServerNotFoundError, UserNotFoundError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(IUserManager)
class UserManager(IUserManager):
    # Same hack as IMessaging.
    bot: Optional[Bot] = None

    def __init__(self, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "UserManager")
    
    async def kick_user(self, server_id: str, user_id: str, reason: str) -> None:
        member = self.get_guild_member(server_id, user_id)
        try:
            await member.kick(reason=reason)
        except Forbidden:
            raise ForbiddenError()

    async def ban_user(self, server_id: str, user_id: str, reason: str, delete_message_days: int = 0) -> None:
        member = self.get_guild_member(server_id, user_id)
        try:
            await member.ban(reason=reason, delete_message_days=delete_message_days)
        except Forbidden:
            raise ForbiddenError()
    
    def get_guild(self, server_id: str) -> Guild:
        if UserManager.bot is None:
            self.__log.warning(f"Bot isn't initialized. {{ ServerId = {server_id} }}")
            raise ValueError("The bot instance isn't initialized.")

        guild: Optional[Guild] = UserManager.bot.get_guild(int(server_id))
        if not guild:
            raise ServerNotFoundError(server_id)
        
        return guild

    def get_guild_member(self, server_id: str, user_id: str) -> Member:
        if UserManager.bot is None:
            self.__log.warning(f"Bot isn't initialized. {{ UserId = {user_id} }}")
            raise ValueError("The bot instance isn't initialized.")

        guild: Optional[Guild] = UserManager.bot.get_guild(int(server_id))
        if not guild:
            raise ServerNotFoundError(server_id)

        member = guild.get_member(int(user_id))
        if not member or not isinstance(member, Member):
            raise UserNotFoundError(user_id)
        
        return member
