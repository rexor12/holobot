from .bot import BotAccessor
from .contexts import IContextManager
from discord import Message as DiscordMessage, Reaction as DiscordReaction, User
from discord.abc import GuildChannel, Messageable, PrivateChannel
from discord.errors import Forbidden, NotFound
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError, MessageNotFoundError
from holobot.discord.sdk.models import Embed, InteractionContext, Message, Reaction
from holobot.discord.transformers.embed import local_to_remote as transform_embed
from holobot.discord.utils import get_user
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import assert_not_none
from typing import Callable, Optional, Union

@injectable(IMessaging)
class Messaging(IMessaging):
    def __init__(self, context_manager: IContextManager, log: LogInterface) -> None:
        super().__init__()
        self.__context_manager: IContextManager = context_manager
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
        except Forbidden:
            raise ForbiddenError()

    async def send_channel_message(self, channel_id: str, message: str) -> None:
        assert_not_none(channel_id, "channel_id")
        assert_not_none(message, "message")

        channel: Optional[Union[GuildChannel, PrivateChannel]] = BotAccessor.get_bot().get_channel(int(channel_id))
        if channel is None or not isinstance(channel, Messageable):
            self.__log.trace(f"Tried to send a guild message to a non-messageable channel. {{ ChannelId = {channel_id}, ChannelType = {type(channel)} }}")
            raise ChannelNotFoundError(channel_id)

        try:
            await channel.send(message)
        except Forbidden:
            raise ForbiddenError()
    
    async def wait_for_reaction(self, filter: Optional[Callable[[Reaction], bool]] = None, timeout: int = 60) -> Reaction:
        discord_filter = Messaging.__create_reaction_filter(filter)
        reaction, user = await BotAccessor.get_bot().wait_for("reaction_add", check=discord_filter, timeout=timeout)
        return Reaction(str(reaction.emoji), str(user.id))

    async def add_reaction(self, context: InteractionContext, message: Message, emoji: str) -> None:
        assert_not_none(context, "context")
        assert_not_none(message, "message")
        assert_not_none(emoji, "emoji")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            await discord_message.add_reaction(emoji)
        except NotFound:
            raise MessageNotFoundError(message.channel_id, message.message_id)
        except Forbidden:
            raise ForbiddenError("No authorization to add reaction.")

    async def remove_reaction(self, context: InteractionContext, message: Message, owner_id: str, emoji: str) -> None:
        assert_not_none(context, "context")
        assert_not_none(message, "message")
        assert_not_none(emoji, "emoji")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            await discord_message.remove_reaction(emoji, get_user(owner_id))
        except NotFound:
            raise MessageNotFoundError(message.channel_id, message.message_id)
        except Forbidden:
            raise ForbiddenError("No authorization to remove reaction.")

    async def edit_message(self, context: InteractionContext, message: Message, content: Union[str, Embed]) -> None:
        assert_not_none(context, "context")
        assert_not_none(message, "message")
        assert_not_none(content, "content")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            if isinstance(content, Embed):
                await discord_message.edit(embed=transform_embed(content))
            else: await discord_message.edit(content=content)
        except NotFound:
            raise MessageNotFoundError(message.channel_id, message.message_id)
        except Forbidden:
            raise ForbiddenError("No authorization to remove reaction.")

    async def send_reply(self, context: InteractionContext, message: Message, content: Union[str, Embed]) -> Message:
        assert_not_none(context, "context")
        assert_not_none(message, "message")
        assert_not_none(content, "content")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            if isinstance(content, Embed):
                reply_message = await discord_message.reply(embed=transform_embed(content))
            else: reply_message = await discord_message.reply(content=content)

            return Message(
                channel_id=str(reply_message.channel.id),
                message_id=str(reply_message.id)
            )
        except NotFound:
            raise MessageNotFoundError(message.channel_id, message.message_id)
        except Forbidden:
            raise ForbiddenError("No authorization to remove reaction.")

    async def send_context_reply(self, context: InteractionContext, content: Union[str, Embed]) -> Message:
        assert_not_none(context, "context")
        assert_not_none(content, "content")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        if isinstance(content, Embed):
            message = await tracked_context.context.reply(embed=transform_embed(content))
        else: message = await tracked_context.context.reply(content=content)
        return Message(
            channel_id=str(message.channel.id),
            message_id=str(message.id)
        )

    async def delete_message(self, context: InteractionContext, message: Message) -> None:
        assert_not_none(context, "context")
        assert_not_none(message, "message")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            await discord_message.delete()
        except NotFound:
            raise MessageNotFoundError(message.channel_id, message.message_id)
        except Forbidden:
            raise ForbiddenError("No authorization to remove reaction.")

    @staticmethod
    def __create_reaction_filter(user_filter: Optional[Callable[[Reaction], bool]]) -> Callable[[DiscordReaction, User], bool]:
        def filter(reaction: DiscordReaction, user: User) -> bool:
            if user_filter is None:
                return True
            return user_filter(Reaction(str(reaction.emoji), str(user.id), str(reaction.message.id)))
        return filter
    
    async def __get_message(self, channel_id: str, message_id: str) -> DiscordMessage:
        channel: Optional[Union[GuildChannel, PrivateChannel]] = BotAccessor.get_bot().get_channel(int(channel_id))
        if not channel:
            raise ChannelNotFoundError(channel_id)

        if not isinstance(channel, Messageable):
            raise TypeError(f"Expected the channel to be '{type(Messageable)}' but got '{type(channel)}'.")

        try:
            return await channel.fetch_message(int(message_id))
        except NotFound:
            raise MessageNotFoundError(channel_id, message_id)
        except Forbidden:
            raise ForbiddenError("No authorization to fetch message.")
