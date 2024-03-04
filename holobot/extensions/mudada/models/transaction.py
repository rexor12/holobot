from dataclasses import dataclass, field
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.utils.datetime_utils import utcnow

@dataclass(kw_only=True)
class Transaction(AggregateRoot[int]):
    """Represents a Mudada transaction."""

    identifier: int = -1
    """The identifier of the entity."""

    created_at: datetime = field(default_factory=utcnow)
    """The date and time at which the transaction was created."""

    owner_id: str
    """The identifier of the user who created the transaction."""

    target_id: str
    """The identifier of the user who receives the funds."""

    amount: int
    """The amount of the currency the transaction carries."""

    message: str | None = None
    """An optional message to be sent to the receiver."""

    is_finalized: bool = False
    """Whether the transaction has been finalized
    and the content can be claimed by the target.
    """

    is_completed: bool = False
    """Whether the transaction has been completed, that is,
    the user has claimed the contents.
    """
