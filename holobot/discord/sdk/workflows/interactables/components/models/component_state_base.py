from dataclasses import dataclass
from typing import Optional

@dataclass(kw_only=True)
class ComponentStateBase:
    owner_id: str 
    """The identifier of the user the component state belongs to."""
