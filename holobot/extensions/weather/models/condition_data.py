from __future__ import annotations

from typing import Any

class ConditionData:
    def __init__(self) -> None:
        self.id = 0
        self.icon = ""
        self.condition_image_url = ""

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        self.__id = value

    @property
    def icon(self) -> str:
        return self.__icon

    @icon.setter
    def icon(self, value: str) -> None:
        self.__icon = value

    @property
    def condition_image_url(self) -> str:
        return self.__condition_image_url

    @condition_image_url.setter
    def condition_image_url(self, value: str) -> None:
        self.__condition_image_url = value

    @staticmethod
    def from_json(json: dict[str, Any]) -> ConditionData:
        entity = ConditionData()
        entity.id = json.get("id", 0)
        entity.icon = json.get("icon", "")
        return entity
