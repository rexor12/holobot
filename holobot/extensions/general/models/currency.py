from dataclasses import dataclass, field
from datetime import datetime

from holobot.extensions.general.sdk.currencies.models import ICurrency
from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.utils.datetime_utils import utcnow

@dataclass(kw_only=True)
class Currency(AggregateRoot[int], ICurrency):
    """Represents a global or server-specific currency."""

    identifier: int = -1
    """The identifier of the currency."""

    created_at: datetime = field(default_factory=utcnow)
    """The date and time at which this currency was created."""

    created_by: int
    """The identifier of the user who created this currency."""

    server_id: int | None
    """The identifier of the server the currency belongs to;
    or, None if it's globally available."""

    name: str
    """The displayed name of the currency."""

    description: str | None = None
    """The displayed description of the currency."""

    emoji_id: int
    """The identifier of the emoji associated to this currency.

    This emoji must be available in the server in which the currency exists.
    If the currency is global, the emoji may come from any server the bot is a member of.
    """

    emoji_name: str
    """The name of the emoji associated to this currency.

    This emoji must be available in the server in which the currency exists.
    If the currency is global, the emoji may come from any server the bot is a member of.
    """

    is_tradable: bool = False
    """Whether or not this currency can be traded between users."""
