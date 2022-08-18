from __future__ import annotations

from typing import Any

class CommandConfiguration:
    def __init__(self, name: str) -> None:
        self.name = name
        self.can_disable = True

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def can_disable(self) -> bool:
        return self.__can_disable

    @can_disable.setter
    def can_disable(self, value: bool) -> None:
        self.__can_disable = value

    @staticmethod
    def from_json(name: str, can_disable_parent: bool, json: dict[str, Any]) -> CommandConfiguration:
        config = CommandConfiguration(name)
        config.can_disable = json.get("CanDisable", can_disable_parent)
        return config
