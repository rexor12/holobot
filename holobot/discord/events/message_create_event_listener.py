import hikari

from holobot.discord.bot import Bot
from holobot.discord.sdk.events import MessageReceivedEvent
from holobot.discord.sdk.models import Message
from holobot.discord.transformers.embed import to_model
from holobot.discord.utils.interaction_utils import ChannelInfo
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
        channel_id, thread_id = MessageCreateEventListener.get_channel_and_thread_ids(event)
        local_event = MessageReceivedEvent(
            message=Message(
                author_id=event.message.author.id,
                server_id=event.message.guild_id,
                channel_id=channel_id,
                thread_id=thread_id,
                message_id=event.message_id,
                content=event.message.content,
                embeds=tuple(map(to_model, event.message.embeds)),
                # No wasting resources on components.
                components=()
            ),
            interaction=None
        )

        for listener in self.__listeners:
            await listener.on_event(local_event)

    @staticmethod
    def get_channel_and_thread_ids(
        event: _EVENT_TYPE
    ) -> ChannelInfo:
        if not isinstance(event, hikari.GuildMessageCreateEvent):
            return ChannelInfo(
                channel_id=event.channel_id,
                thread_id=None
            )

        channel = event.get_channel()
        channel_id = event.channel_id
        thread_id = None
        if isinstance(channel, hikari.GuildThreadChannel):
            channel_id = channel.parent_id
            thread_id = event.channel_id

        return ChannelInfo(
            channel_id=channel_id,
            thread_id=thread_id
        )
