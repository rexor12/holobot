from __future__ import annotations
from .child_command_builder import ChildCommandBuilder
from hikari.api.special_endpoints import SlashCommandBuilder
from typing import Callable

import hikari

class CommandSubGroupBuilder:
    @property
    def parent(self) -> CommandGroupBuilder:
        return self.__parent_builder

    def __init__(
        self,
        name: str,
        description: str,
        parent_builder: CommandGroupBuilder) -> None:
        self.__name: str = name
        self.__description: str = description
        self.__parent_builder: CommandGroupBuilder = parent_builder
        self.__commands: dict[str, ChildCommandBuilder[CommandSubGroupBuilder]] = {}

    def with_command(self, name: str, description: str) -> ChildCommandBuilder[CommandSubGroupBuilder]:
        if name in self.__commands:
            raise ValueError(f"There is already a sub-group command added with the name '{name}'.")
        self.__commands[name] = builder = ChildCommandBuilder[CommandSubGroupBuilder](name, description, self)
        return builder

    def build(self) -> hikari.CommandOption:
        return hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND_GROUP,
            name=self.__name,
            description=self.__description,
            options=[command.build() for command in self.__commands.values()]
        )

class CommandGroupBuilder:
    def __init__(
        self,
        name: str,
        description: str,
        slash_command_builder_factory: Callable[[str, str], SlashCommandBuilder]) -> None:
        self.__name: str = name
        self.__description: str = description
        self.__slash_command_builder_factory: Callable[[str, str], SlashCommandBuilder] = slash_command_builder_factory
        self.__sub_groups: dict[str, CommandSubGroupBuilder] = {}
        self.__commands: dict[str, ChildCommandBuilder[CommandGroupBuilder]] = {}

    def with_command(self, name: str, description: str) -> ChildCommandBuilder[CommandGroupBuilder]:
        if name in self.__commands:
            raise ValueError(f"There is already a group command added with the name '{name}'.")
        self.__commands[name] = builder = ChildCommandBuilder[CommandGroupBuilder](name, description, self)
        return builder

    def with_sub_group(self, name: str, description: str) -> CommandSubGroupBuilder:
        if name in self.__sub_groups:
            raise ValueError(f"There is already a sub-group added with the name '{name}'.")
        self.__sub_groups[name] = builder = CommandSubGroupBuilder(name, description, self)
        return builder

    def build(self) -> SlashCommandBuilder:
        builder = self.__slash_command_builder_factory(self.__name, self.__description)
        for sub_group in self.__sub_groups.values():
            builder.add_option(sub_group.build())
        for command in self.__commands.values():
            builder.add_option(command.build())
        return builder
