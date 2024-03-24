import hikari

from holobot.discord.bot import Bot
from holobot.discord.sdk.events import MessageReceivedEvent
from holobot.discord.sdk.models import InteractionInfo, Message
from holobot.discord.transformers.embed import to_model
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener
from .discord_event_listener_base import DiscordEventListenerBase
from .igeneric_discord_event_listener import IGenericDiscordEventListener

_EVENT_TYPE = hikari.MessageCreateEvent

@injectable(IGenericDiscordEventListener)
class MessageCreateEventListener(DiscordEventListenerBase[_EVENT_TYPE]):
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
            message=Message(
                author_id=str(event.message.author.id),
                server_id=str(event.message.guild_id) if event.message.guild_id else None,
                channel_id=str(event.message.channel_id),
                message_id=str(event.message_id),
                content=event.message.content,
                embeds=tuple(map(to_model, event.message.embeds)),
                # We're lazy so components aren't parsed for regular messages.
                components=()
            ),
            interaction=MessageCreateEventListener.__create_interaction_info(event)
        )

        for listener in self.__listeners:
            await listener.on_event(local_event)

    @staticmethod
    def __create_interaction_info(event: _EVENT_TYPE) -> InteractionInfo | None:
        if not (interaction := event.message.interaction):
            return None

        return InteractionInfo(
            author_id=str(interaction.user.id),
            name=interaction.name
        )
