from dataclasses import dataclass
from datetime import datetime

@dataclass
class Server:
    """Holds basic information about a server."""

    identifier: int
    """The identifier of the server."""

    owner_id: int | None
    """The identifier of the server owner."""

    owner_name: str | None
    """The name of the server owner."""

    name: str
    """The name of the server."""

    member_count: int | None
    """The number of members the server has.

    In cases of large servers, this information may be unavailable.
    """

    icon_url: str | None
    """The URL of the server's icon."""

    is_large: bool | None
    """Whether the server is a large server.

    Large servers are servers with more than 75 000 members.
    """

    joined_at: datetime | None
    """The date and time at which the bot joined the server."""

    shard_id: int | None
    """The identifier of the shard serving this server."""
