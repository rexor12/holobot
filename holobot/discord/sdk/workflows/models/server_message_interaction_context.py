from dataclasses import dataclass
from typing import Optional

from holobot.discord.sdk.models import InteractionContext

@dataclass
class ServerMessageInteractionContext(InteractionContext):
    """A context for server-specific message context menu interactions."""

    server_id: str
    server_name: Optional[str]
    channel_id: str
    target_message_id: str
