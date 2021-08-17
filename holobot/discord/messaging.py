from .bot import Bot
from discord import Reaction as DiscordReaction, User
from discord.abc import GuildChannel, Messageable, PrivateChannel
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.models import Reaction
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Callable, Optional, Union

@injectable(IMessaging)
class Messaging(IMessaging):
    # NOTE: This is a hack, because we have a circular dependency here.
    # Messages can be sent through an instance of Bot only, but
    # in our particular case, Bot uses cogs which use services
    # that require the messaging - which needs a Bot!
    # Therefore, as a hack, we're using this static field
    # to have a reference to our instance of Bot... at some point.
    # This could possibly be avoided if discord.py supported IoC.
    bot: Optional[Bot] = None

    def __init__(self, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "Messaging")
    
    async def send_dm(self, user_id: str, message: str) -> None:
        if Messaging.bot is None:
            self.__log.warning(f"Bot isn't initialized. {{ UserId = {user_id}, Operation = DM }}")
            return
        if not (user := Messaging.bot.get_user_by_id(int(user_id))):
            self.__log.warning(f"Inexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        self.__log.trace(f"Sending DM... {{ UserId = {user_id} }}")
        await user.send(message)

    async def wait_for_reaction(self, filter: Optional[Callable[[Reaction], bool]] = None, timeout: int = 60) -> Reaction:
        if Messaging.bot is None:
            self.__log.error(f"Bot isn't initialized. {{ Operation = AwaitReaction }}")
            # TODO Specific exception. Also, handle it.
            raise ValueError("Messaging isn't initialized yet.")

        discord_filter = Messaging.__create_reaction_filter(filter)
        reaction, user = await Messaging.bot.wait_for("reaction_add", check=discord_filter, timeout=timeout)
        return Reaction(str(reaction.emoji), str(user.id))

    async def send_guild_message(self, channel_id: str, message: str) -> None:
        if Messaging.bot is None:
            self.__log.error(f"Bot isn't initialized. {{ Operation = SendGuildMessage }}")
            # TODO Specific exception. Also, handle it.
            raise ValueError("Messaging isn't initialized yet.")

        channel: Optional[Union[GuildChannel, PrivateChannel]] = Messaging.bot.get_channel(int(channel_id))
        if channel is None or not isinstance(channel, Messageable):
            self.__log.trace(f"Tried to send a guild message to a non-messageable channel. {{ ChannelId = {channel_id}, ChannelType = {type(channel)} }}")
            return # TODO Raise an error.

        await channel.send(message)
    
    @staticmethod
    def __create_reaction_filter(user_filter: Optional[Callable[[Reaction], bool]]) -> Callable[[DiscordReaction, User], bool]:
        def filter(reaction: DiscordReaction, user: User) -> bool:
            if user_filter is None:
                return True
            return user_filter(Reaction(str(reaction.emoji), str(user.id), str(reaction.message.id)))
        return filter
