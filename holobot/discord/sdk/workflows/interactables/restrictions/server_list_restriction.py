from dataclasses import dataclass, field

from .restriction_base import RestrictionBase

@dataclass(kw_only=True)
class ServerListRestriction(RestrictionBase):
    """A restriction that requires the server's identifier
    to be one of a pre-defined list of server identifiers
    for the associated interactable to be allowed."""

    server_ids: set[int] = field(default_factory=set)
    """A set of server identifiers for which the interactable should be available."""
