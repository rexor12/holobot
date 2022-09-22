from hikari import (
    UNDEFINED, ForbiddenError as HikariForbiddenError, GuildNewsChannel, TextableGuildChannel
)

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError, InvalidChannelError
from holobot.discord.sdk.models.embed import Embed
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, LayoutBase
from holobot.discord.transformers.embed import to_dto as embed_to_dto
from holobot.discord.utils import get_guild_channel
from holobot.discord.workflows.transformers import IComponentTransformer
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import assert_not_none
from .bot import get_bot

@injectable(IMessaging)
class Messaging(IMessaging):
    def __init__(
        self,
        component_transformer: IComponentTransformer,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__component_transformer = component_transformer
        self.__log = logger_factory.create(Messaging)

    async def send_private_message(self, user_id: str, message: str) -> None:
        assert_not_none(user_id, "user_id")
        assert_not_none(message, "message")

        if not (user := get_bot().get_user_by_id(int(user_id))):
            self.__log.warning("Failed to DM invalid user", user_id=user_id)
            return
        self.__log.trace("Sending DM...", user_id=user_id)
        try:
            await user.send(message)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot send DMs to the specified user.") from error

    async def send_channel_message(
        self,
        server_id: str,
        channel_id: str,
        content: str | Embed,
        components: ComponentBase | list[LayoutBase] | None = None
    ) -> str:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(content, "content")

        channel = get_guild_channel(server_id, channel_id)
        if not channel or not isinstance(channel, TextableGuildChannel):
            self.__log.trace(
                "Tried to send a guild message to a non-messageable channel",
                channel_id=channel_id,
                channel_type=type(channel)
            )
            raise ChannelNotFoundError(channel_id)

        text_content = content if isinstance(content, str) else UNDEFINED
        embed_content = embed_to_dto(content) if isinstance(content, Embed) else UNDEFINED
        try:
            message = await channel.send(
                content=text_content,
                embed=embed_content,
                components=(
                    self.__component_transformer.transform_to_root_component(components)
                    if components else UNDEFINED
                )
            )

            return str(message.id)
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot send messages to the specified channel.") from error

    async def crosspost_message(
        self,
        server_id: str,
        channel_id: str,
        message_id: str
    ) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(message_id, "message_id")

        channel = get_guild_channel(server_id, channel_id)
        if not isinstance(channel, GuildNewsChannel):
            raise InvalidChannelError(
                server_id,
                channel_id,
                "The source channel must be a news-type channel."
            )

        await get_bot().rest.crosspost_message(channel, int(message_id))
