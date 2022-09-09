from __future__ import annotations

from dataclasses import dataclass, field

_PRIMITIVE_TYPE = str | int | bool | float
_COMPLEX_TYPE = _PRIMITIVE_TYPE | list[_PRIMITIVE_TYPE] | dict[str | int, _PRIMITIVE_TYPE]

@dataclass(kw_only=True, frozen=True)
class JsonObject:
    properties: dict[str | int, JsonObject | _COMPLEX_TYPE] = field(default_factory=dict)
