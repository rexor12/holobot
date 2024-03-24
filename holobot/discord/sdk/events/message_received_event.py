from dataclasses import dataclass

from holobot.discord.sdk.models import InteractionInfo, Message
from holobot.sdk.reactive.models import EventBase

@dataclass(kw_only=True, frozen=True)
class MessageReceivedEvent(EventBase):
    message: Message
    interaction: InteractionInfo | None
