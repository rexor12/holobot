from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(kw_only=True, frozen=True)
class I18nGroup:
    name: str
    value: dict[str, I18nGroup | str | tuple[str, ...]] = field(default_factory=dict)
