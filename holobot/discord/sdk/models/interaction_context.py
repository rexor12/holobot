from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class InteractionContext:
    """A base context for interactions."""

    request_id: UUID
    author_id: str
    author_name: str
    author_nickname: Optional[str]
