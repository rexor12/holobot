from dataclasses import dataclass

from holobot.discord.sdk.models import InteractionContext

@dataclass
class ServerUserInteractionContext(InteractionContext):
    """A context for server-specific user context menu interactions."""

    server_id: int
    server_name: str | None
    channel_id: int
    target_user_id: int
