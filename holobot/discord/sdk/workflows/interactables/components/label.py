from dataclasses import dataclass

from .component_base import ComponentBase

@dataclass(kw_only=True)
class Label(ComponentBase):
    """A component that displays formatted text."""

    content: str
    """The content of the label. It supports markdown and multiple lines."""
