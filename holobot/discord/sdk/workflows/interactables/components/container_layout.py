from dataclasses import dataclass

from .label import Label
from .layout_base import LayoutBase
from .section_layout import SectionLayout
from .separator import Separator
from .stack_layout import StackLayout

@dataclass(kw_only=True)
class ContainerLayout(LayoutBase[StackLayout | Label | SectionLayout | Separator]): # TODO | media gallery | file
    """A layout component that contains other components, similar in looks to an embed."""

    accent_color: int | None = None
    """An optional colored bar to be displayed on the left side of the container."""

    is_spoiler: bool = False
    """Whether the container should be marked as spoiler."""
