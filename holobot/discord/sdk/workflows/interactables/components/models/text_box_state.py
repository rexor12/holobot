from collections.abc import Sequence
from dataclasses import dataclass, field

from .component_state_base import ComponentStateBase

@dataclass(kw_only=True)
class TextBoxState(ComponentStateBase):
    """Represents the state of a text box."""

    value: str | None = None
    """The value that has been entered in the text box."""

    custom_data: dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.value if self.value is not None else "<No value>"
