from dataclasses import dataclass

from holobot.discord.sdk.models import InteractionContext

@dataclass
class ServerMessageInteractionContext(InteractionContext):
    """A context for server-specific message context menu interactions."""

    server_id: int
    server_name: str | None
    channel_id: int
    target_message_id: int
