from dataclasses import dataclass

from holobot.discord.sdk.models import InteractionContext

@dataclass
class DirectMessageInteractionContext(InteractionContext):
    """A context for direct message-specific chat interactions."""

    channel_id: int
