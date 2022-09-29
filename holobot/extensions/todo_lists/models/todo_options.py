from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class TodoOptions(OptionsDefinition):
    section_name: ClassVar[str] = "TodoLists"

    TodoItemsPerUserMax: int = 10
    MessageLengthMin: int = 10
    MessageLengthMax: int = 192
