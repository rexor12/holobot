from .command_tags import CommandTag, DeleteCommandTag, InsertCommandTag, UpdateCommandTag
from holobot.sdk.utils import assert_not_none
from typing import Any, Generic, TypeVar

TTag = TypeVar("TTag", bound=CommandTag)

class CommandComplete(Generic[TTag]):
    def __init__(self, command_tag: TTag) -> None:
        self.__command_tag: TTag = command_tag

    @property
    def command_tag(self) -> TTag:
        return self.__command_tag

    @staticmethod
    def parse(value: str) -> 'CommandComplete[Any]':
        assert_not_none(value, "value")

        parts = value.split(" ")
        if parts[0] == "INSERT":
            tag = InsertCommandTag(parts[1], int(parts[2]), value)
        elif parts[0] == "DELETE":
            tag = DeleteCommandTag(int(parts[1]), value)
        elif parts[0] == "UPDATE":
            tag = UpdateCommandTag(int(parts[1]), value)
        else: tag = CommandTag(value)
        
        return CommandComplete(tag)
    
    def __repr__(self) -> str:
        return "CommandComplete(%r)" % self.__command_tag
