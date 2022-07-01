from .bot import BotAccessor
from hikari import (
    ForbiddenError as HikariForbiddenError,
    TextableGuildChannel
)
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError
from holobot.discord.utils import get_guild_channel
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import assert_not_none

@injectable(IMessaging)
class Messaging(IMessaging):
    def __init__(self, log: LogInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "Messaging")

    async def send_private_message(self, user_id: str, message: str) -> None:
        assert_not_none(user_id, "user_id")
        assert_not_none(message, "message")

        if not (user := BotAccessor.get_bot().get_user_by_id(int(user_id))):
            self.__log.warning(f"Inexistent user. {{ UserId = {user_id}, Operation = DM }}")
            return
        self.__log.trace(f"Sending DM... {{ UserId = {user_id} }}")
        try:
            await user.send(message)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot send DMs to the specified user.") from error

    async def send_channel_message(self, server_id: str, channel_id: str, message: str) -> None:
        assert_not_none(channel_id, "channel_id")
        assert_not_none(message, "message")

        channel = get_guild_channel(server_id, channel_id)
        if not channel or not isinstance(channel, TextableGuildChannel):
            self.__log.trace(f"Tried to send a guild message to a non-messageable channel. {{ ChannelId = {channel_id}, ChannelType = {type(channel)} }}")
            raise ChannelNotFoundError(channel_id)

        try:
            await channel.send(message)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot send messages to the specified channel.") from error
