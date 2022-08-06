from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Server:
    """Holds basic information about a server."""

    identifier: str
    """The identifier of the server."""

    owner_id: Optional[str]
    """The identifier of the server owner."""

    owner_name: Optional[str]
    """The name of the server owner."""

    name: str
    """The name of the server."""

    member_count: Optional[int]
    """The number of members the server has.

    In cases of large servers, this information may be unavailable.
    """

    icon_url: Optional[str]
    """The URL of the server's icon."""

    is_large: Optional[bool]
    """Whether the server is a large server.

    Large servers are servers with more than 75 000 members.
    """

    joined_at: Optional[datetime]
    """The date and time at which the bot joined the server."""

    shard_id: Optional[int]
    """The identifier of the shard serving this server."""
