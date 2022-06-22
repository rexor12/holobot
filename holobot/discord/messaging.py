from .bot import BotAccessor
from .contexts import IContextManager
from hikari import (
    ComponentInteraction,
    ForbiddenError as HikariForbiddenError,
    GuildChannel,
    Message as HikariMessage,
    NotFoundError as HikariNotFoundError,
    ReactionAddEvent,
    TextableGuildChannel
)
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError, MessageNotFoundError
from holobot.discord.sdk.models import Embed, InteractionContext, Message, Reaction
from holobot.discord.transformers.embed import to_dto as transform_embed
from holobot.discord.utils import get_guild_channel, get_guild, get_user
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

    async def wait_for_reaction(self, filter: Optional[Callable[[Reaction], bool]] = None, timeout: int = 60) -> Reaction:
        predicate = Messaging.__create_reaction_filter(filter)
        reaction = await BotAccessor.get_bot().wait_for(ReactionAddEvent, timeout=timeout, predicate=predicate)
        return Reaction(str(reaction.emoji_id), str(reaction.user_id))

    async def add_reaction(self, context: InteractionContext, message: Message, emoji: str) -> None:
        assert_not_none(context, "context")
        assert_not_none(message, "message")
        assert_not_none(emoji, "emoji")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            await discord_message.add_reaction(emoji)
        except HikariNotFoundError as error:
            raise MessageNotFoundError(message.channel_id, message.message_id) from error
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot add reactions to the specified message.") from error

    async def remove_reaction(self, context: InteractionContext, message: Message, owner_id: str, emoji: str) -> None:
        assert_not_none(context, "context")
        assert_not_none(message, "message")
        assert_not_none(emoji, "emoji")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            await discord_message.remove_reaction(emoji, user=get_user(owner_id))
        except HikariNotFoundError as error:
            raise MessageNotFoundError(message.channel_id, message.message_id) from error
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot remove reactions from the specified message.") from error

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
        except HikariNotFoundError as error:
            raise MessageNotFoundError(message.channel_id, message.message_id) from error
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot edit the specified message.") from error

    async def send_reply(self, context: InteractionContext, message: Message, content: Union[str, Embed]) -> Message:
        assert_not_none(context, "context")
        assert_not_none(message, "message")
        assert_not_none(content, "content")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            if isinstance(discord_message, HikariMessage):
                # TODO Proper error.
                raise ValueError("The target message is of the wrong type.")

            if isinstance(content, Embed):
                reply_message = await discord_message.respond(embed=transform_embed(content), reply=discord_message.id)
            else: reply_message = await discord_message.respond(content=content, reply=discord_message.id)

            return Message(
                server_id=str(reply_message.guild_id) if reply_message.guild_id else None,
                channel_id=str(reply_message.channel_id),
                message_id=str(reply_message.id)
            )
        except HikariNotFoundError as error:
            raise MessageNotFoundError(message.channel_id, message.message_id) from error
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot send reply to the specified message.") from error

    async def send_context_reply(self, context: InteractionContext, content: Union[str, Embed]) -> Message:
        assert_not_none(context, "context")
        assert_not_none(content, "content")

        # TODO Make this work again.
        raise NotImplementedError
        # tracked_context = await self.__context_manager.get_context(context.request_id)
        # if isinstance(content, Embed):
        #     message = await tracked_context.context.reply(embed=transform_embed(content))
        # else: message = await tracked_context.context.reply(content=content)
        # return Message(
        #     channel_id=str(message.channel.id),
        #     message_id=str(message.id)
        # )

    async def delete_message(self, context: InteractionContext, message: Message) -> None:
        assert_not_none(context, "context")
        assert_not_none(message, "message")

        tracked_context = await self.__context_manager.get_context(context.request_id)
        discord_message = await tracked_context.get_or_add_message(message.channel_id, message.message_id, self.__get_message)
        try:
            await discord_message.delete()
        except HikariNotFoundError as error:
            raise MessageNotFoundError(message.channel_id, message.message_id) from error
        except HikariForbiddenError as error:
            raise ForbiddenError("Cannot delete the specified message.") from error

    @staticmethod
    def __create_reaction_filter(user_filter: Optional[Callable[[Reaction], bool]]) -> Callable[[ReactionAddEvent], bool]:
        def reaction_filter(reaction: ReactionAddEvent) -> bool:
            if user_filter is None:
                return True
            return user_filter(Reaction(str(reaction.emoji_id), str(reaction.user_id), str(reaction.message_id)))
        return reaction_filter
    
    async def __get_message(self, channel_id: str, message_id: str) -> HikariMessage:
        # TODO Fix this for pager stuff. Or just change the pager ffs.
        raise NotImplementedError
        # channel: Optional[GuildChannel] = BotAccessor.get_bot().get_channel(int(channel_id))
        # if not channel:
        #     raise ChannelNotFoundError(channel_id)

        # if not isinstance(channel, Messageable):
        #     raise TypeError(f"Expected the channel to be '{type(Messageable)}' but got '{type(channel)}'.")

        # try:
        #     return await channel.fetch_message(int(message_id))
        # except HikariNotFoundError as error:
        #     raise MessageNotFoundError(channel_id, message_id) from error
        # except HikariForbiddenError as error:
        #     raise ForbiddenError("Cannot fetch the specified message.") from error
