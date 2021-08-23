from .bot import BotAccessor
from discord import Reaction as DiscordReaction, User
from discord.abc import GuildChannel, Messageable, PrivateChannel
from discord.errors import Forbidden
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError
from holobot.discord.sdk.models import Reaction
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Callable, Optional, Union

@injectable(IMessaging)
class Messaging(IMessaging):
    def __init__(self, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "Messaging")
    
    async def send_private_message(self, user_id: str, message: str) -> None:
        if not (user := BotAccessor.get_bot().get_user_by_id(int(user_id))):
            self.__log.warning(f"Inexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        self.__log.trace(f"Sending DM... {{ UserId = {user_id} }}")
        try:
            await user.send(message)
        except Forbidden:
            raise ForbiddenError()

    async def wait_for_reaction(self, filter: Optional[Callable[[Reaction], bool]] = None, timeout: int = 60) -> Reaction:
        discord_filter = Messaging.__create_reaction_filter(filter)
        reaction, user = await BotAccessor.get_bot().wait_for("reaction_add", check=discord_filter, timeout=timeout)
        return Reaction(str(reaction.emoji), str(user.id))

    async def send_channel_message(self, channel_id: str, message: str) -> None:
        channel: Optional[Union[GuildChannel, PrivateChannel]] = BotAccessor.get_bot().get_channel(int(channel_id))
        if channel is None or not isinstance(channel, Messageable):
            self.__log.trace(f"Tried to send a guild message to a non-messageable channel. {{ ChannelId = {channel_id}, ChannelType = {type(channel)} }}")
            raise ChannelNotFoundError(channel_id)

        try:
            await channel.send(message)
        except Forbidden:
            raise ForbiddenError()
    
    @staticmethod
    def __create_reaction_filter(user_filter: Optional[Callable[[Reaction], bool]]) -> Callable[[DiscordReaction, User], bool]:
        def filter(reaction: DiscordReaction, user: User) -> bool:
            if user_filter is None:
                return True
            return user_filter(Reaction(str(reaction.emoji), str(user.id), str(reaction.message.id)))
        return filter
