from dataclasses import dataclass

@dataclass(kw_only=True)
class ViewBase:
    """Base class for a view."""

    identifier: str
    """The identifier of this view, which is used for handling callbacks."""

    owner_id: int
    """The identifier of the user who owns the view."""
