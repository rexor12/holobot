from dataclasses import dataclass
from typing import Optional

from holobot.discord.sdk.models import InteractionContext

@dataclass
class ServerUserInteractionContext(InteractionContext):
    """A context for server-specific user context menu interactions."""

    server_id: str
    server_name: Optional[str]
    channel_id: str
    target_user_id: str
