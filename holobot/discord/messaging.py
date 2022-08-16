from hikari import ForbiddenError as HikariForbiddenError, TextableGuildChannel

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError
from holobot.discord.utils import get_guild_channel
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import assert_not_none
from .bot import BotAccessor

@injectable(IMessaging)
class Messaging(IMessaging):
    def __init__(self, logger_factory: ILoggerFactory) -> None:
        super().__init__()
        self.__log = logger_factory.create(Messaging)

    async def send_private_message(self, user_id: str, message: str) -> None:
        assert_not_none(user_id, "user_id")
        assert_not_none(message, "message")

        if not (user := BotAccessor.get_bot().get_user_by_id(int(user_id))):
            self.__log.warning("Failed to DM invalid user", user_id=user_id)
            return
        self.__log.trace("Sending DM...", user_id=user_id)
        try:
            await user.send(message)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot send DMs to the specified user.") from error

    async def send_channel_message(self, server_id: str, channel_id: str, message: str) -> None:
        assert_not_none(channel_id, "channel_id")
        assert_not_none(message, "message")

        channel = get_guild_channel(server_id, channel_id)
        if not channel or not isinstance(channel, TextableGuildChannel):
            self.__log.trace(
                "Tried to send a guild message to a non-messageable channel",
                channel_id=channel_id,
                channel_type=type(channel)
            )
            raise ChannelNotFoundError(channel_id)

        try:
            await channel.send(message)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot send messages to the specified channel.") from error
