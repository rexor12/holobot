from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(kw_only=True, frozen=True)
class I18nGroup:
    name: str
    value: dict[str, I18nGroup | str | tuple[str, ...]] = field(default_factory=dict)

    def merge(self, other: I18nGroup) -> None:
        for key, other_value in other.value.items():
            if key not in self.value:
                self.value[key] = other_value
                continue

            existing_value = self.value[key]
            if (
                isinstance(existing_value, I18nGroup)
                and isinstance(other_value, I18nGroup)
            ):
                existing_value.merge(other_value)
                continue

            self.value[key] = other_value
