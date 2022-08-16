from dataclasses import dataclass
from uuid import UUID

@dataclass
class InteractionContext:
    """A base context for interactions."""

    request_id: UUID
    author_id: str
    author_name: str
    author_nickname: str | None
