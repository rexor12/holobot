from dataclasses import dataclass
from holobot.discord.sdk.models import InteractionContext
from typing import Optional

@dataclass
class ServerUserInteractionContext(InteractionContext):
    """A context for server-specific user context menu interactions."""

    server_id: str
    server_name: Optional[str]
    channel_id: str
    target_user_id: str
