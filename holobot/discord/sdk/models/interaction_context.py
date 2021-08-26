from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass
class InteractionContext:
    """A base context for interactions."""

    request_id: UUID = field(default_factory=lambda: uuid4())
    author_id: str = ""
    author_name: str = ""
