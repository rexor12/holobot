from collections.abc import Callable
from typing import cast

import hikari

from holobot.discord.bot import Bot
from holobot.discord.exceptions import UnknownInteractionTypeException
from holobot.discord.sdk.events import MessageReceivedEvent
from holobot.discord.sdk.models import InteractionInfo, Message
from holobot.discord.transformers.embed import to_model
from holobot.discord.utils.interaction_utils import get_channel_and_thread_ids
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener
from .discord_event_listener_base import DiscordEventListenerBase
from .igeneric_discord_event_listener import IGenericDiscordEventListener

_EVENT_TYPE = hikari.InteractionCreateEvent

_INTERACTION_NAME_GETTERS: dict[type, Callable[[hikari.PartialInteraction], str]] = {
    hikari.AutocompleteInteraction: lambda i: cast(hikari.AutocompleteInteraction, i).command_name,
    hikari.CommandInteraction: lambda i: cast(hikari.CommandInteraction, i).command_name,
    hikari.ComponentInteraction: lambda i: cast(hikari.ComponentInteraction, i).custom_id,
    hikari.ModalInteraction: lambda i: cast(hikari.ModalInteraction, i).custom_id
}

_MESSAGE_GETTERS: dict[type, Callable[[hikari.PartialInteraction], hikari.Message | None]] = {
    hikari.AutocompleteInteraction: lambda _: None,
    hikari.CommandInteraction: lambda _: None,
    hikari.ComponentInteraction: lambda i: cast(hikari.ComponentInteraction, i).message,
    hikari.ModalInteraction: lambda i: cast(hikari.ModalInteraction, i).message
}

@injectable(IGenericDiscordEventListener)
class ProcessListenersOnInteractionCreate(DiscordEventListenerBase[_EVENT_TYPE]):
    @property
    def event_type(self) -> type:
        return _EVENT_TYPE

    def __init__(
        self,
        listeners: tuple[IListener[MessageReceivedEvent], ...]
    ) -> None:
        super().__init__()
        self.__listeners = sorted(listeners, key=lambda i: i.priority)

    async def on_event(self, bot: Bot, event: _EVENT_TYPE) -> None:
        local_event = MessageReceivedEvent(
            message=ProcessListenersOnInteractionCreate.__create_message(event),
            interaction=ProcessListenersOnInteractionCreate.__create_interaction_info(event)
        )

        for listener in self.__listeners:
            await listener.on_event(local_event)

    @staticmethod
    def __create_interaction_info(event: _EVENT_TYPE) -> InteractionInfo | None:
        if not (interaction := event.interaction):
            return None

        if not (name_getter := _INTERACTION_NAME_GETTERS.get(type(event.interaction), None)):
            raise UnknownInteractionTypeException(type(interaction))

        return InteractionInfo(
            author_id=interaction.user.id,
            name=name_getter(event.interaction)
        )

    @staticmethod
    def __create_message(
        event: _EVENT_TYPE
    ) -> Message:
        channel_id, thread_id = get_channel_and_thread_ids(event.interaction)
        if not (message_getter := _MESSAGE_GETTERS.get(type(event.interaction), None)):
            raise UnknownInteractionTypeException(type(event.interaction))

        if message := message_getter(event.interaction):
            message_id = message.id
            message_content = message.content
            message_embeds = tuple(map(to_model, message.embeds))
        else:
            message_id = None
            message_content = None
            message_embeds = ()

        return Message(
            author_id=event.interaction.user.id,
            server_id=event.interaction.guild_id,
            channel_id=channel_id,
            thread_id=thread_id,
            message_id=message_id,
            content=message_content,
            embeds=message_embeds,
            # No wasting resources on components.
            components=()
        )
