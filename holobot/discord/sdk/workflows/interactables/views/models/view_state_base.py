from dataclasses import dataclass

@dataclass(kw_only=True)
class ViewStateBase:
    """Base class for view states."""

    owner_id: int
    """The identifier of the user the view state belongs to."""
