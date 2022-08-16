from dataclasses import dataclass

from .layout import Layout

@dataclass(kw_only=True)
class StackLayout(Layout):
    pass
