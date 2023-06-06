from dataclasses import dataclass
from uuid import UUID

from .message import Message

@dataclass
class InteractionContext:
    """A base context for interactions."""

    request_id: UUID
    author_id: str
    author_name: str
    author_nickname: str | None
    message: Message | None

    @property
    def author_display_name(self) -> str:
        return self.author_nickname or self.author_name
