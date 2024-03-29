from dataclasses import dataclass

from holobot.discord.sdk.models import InteractionContext

@dataclass
class ServerChatInteractionContext(InteractionContext):
    """A context for server-specific chat interactions."""

    server_id: str
    server_name: str
    channel_id: str
