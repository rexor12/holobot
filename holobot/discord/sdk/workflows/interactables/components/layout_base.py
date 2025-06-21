from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .component_base import ComponentBase

TChildren = TypeVar("TChildren", bound=ComponentBase)

@dataclass(kw_only=True)
class LayoutBase(Generic[TChildren], ComponentBase):
    children: list[TChildren] = field(default_factory=list)
