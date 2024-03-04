from dataclasses import dataclass, field
from datetime import datetime, timedelta

from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.utils.datetime_utils import utcnow

@dataclass(kw_only=True)
class ChannelTimer(AggregateRoot[int]):
    """Represents a channel timer."""

    identifier: int = -1
    """The identifier of the entity."""

    user_id: str
    """The identifier of the user who set up the timer."""

    server_id: str
    """The identifier of the server that contains the target channel."""

    channel_id: str
    """The identifier of the channel to be used as a timer."""

    base_time: datetime = field(default_factory=utcnow)
    """The date and time to use as the relative starting point."""

    countdown_interval: timedelta
    """The interval of the timer."""

    name_template: str | None
    """The template for the channel's name.

    Use `%t` as the placeholder for the formatted time (eg. 3d 27h 45m).
    """

    expiry_name_template: str | None
    """The template for the channel's name when less than 5 minutes are left.

    The `%t` placeholder is not valid here.
    """
