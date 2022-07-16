from __future__ import annotations
from typing import Generic, List, TypeVar

import hikari

from .utils import transform_option
from holobot.discord.sdk.workflows.interactables.models import Option

TParentBuilder = TypeVar("TParentBuilder")

class ChildCommandBuilder(Generic[TParentBuilder]):
    @property
    def parent(self) -> TParentBuilder:
        return self.__parent_builder

    def __init__(self, name: str, description: str, parent_builder: TParentBuilder) -> None:
        super().__init__()
        self.__name: str = name
        self.__description: str = description
        self.__parent_builder: TParentBuilder = parent_builder
        self.__options: List[Option] = []

    def with_option(self, option: Option) -> ChildCommandBuilder[TParentBuilder]:
        self.__options.append(option)
        return self

    def build(self) -> hikari.CommandOption:
        return hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND,
            name=self.__name,
            description=self.__description,
            options=[
                transform_option(option)
                for option in self.__options
            ]
        )
