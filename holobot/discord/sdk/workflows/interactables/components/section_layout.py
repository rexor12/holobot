from dataclasses import dataclass

from .button import Button
from .label import Label
from .layout_base import LayoutBase
from .thumbnail import Thumbnail

@dataclass(kw_only=True)
class SectionLayout(LayoutBase[Label]):
    """A layout component that can display multiple labels and an accessory."""

    accessory: Thumbnail | Button
    """An accessory to display alongside the label(s)."""
