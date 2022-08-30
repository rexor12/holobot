from __future__ import annotations

from typing import Any, Generic, TypeVar

from holobot.sdk.utils import assert_not_none
from .command_tags import CommandTag, DeleteCommandTag, InsertCommandTag, UpdateCommandTag

TTag = TypeVar("TTag", bound=CommandTag)

class CommandComplete(Generic[TTag]):
    def __init__(self, command_tag: TTag) -> None:
        self.__command_tag: TTag = command_tag

    @property
    def command_tag(self) -> TTag:
        return self.__command_tag

    @staticmethod
    def parse(value: str) -> CommandComplete[Any]:
        assert_not_none(value, "value")

        parts = value.split(" ")
        match parts[0]:
            case "INSERT":
                tag = InsertCommandTag(parts[1], int(parts[2]), value)
            case "DELETE":
                tag = DeleteCommandTag(int(parts[1]), value)
            case "UPDATE":
                tag = UpdateCommandTag(int(parts[1]), value)
            case _:
                tag = CommandTag(value)

        return CommandComplete(tag)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__command_tag!r})"
