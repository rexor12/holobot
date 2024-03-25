from __future__ import annotations

from collections.abc import Callable

from hikari.api.special_endpoints import SlashCommandBuilder

from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows.interactables.models import Option
from holobot.discord.utils.permission_utils import map_permissions_to_dtos
from .utils import transform_option

class CommandBuilder:
    def __init__(
        self,
        name: str,
        description: str,
        slash_command_builder_factory: Callable[[str, str], SlashCommandBuilder]
    ) -> None:
        self.__name = name
        self.__description = description
        self.__slash_command_builder_factory = slash_command_builder_factory
        self.__options = list[Option]()
        self.__permissions = Permission.NONE

    def with_option(self, option: Option) -> CommandBuilder:
        self.__options.append(option)
        return self

    def with_default_permissions(self, permissions: Permission):
        self.__permissions = permissions
        return self

    def build(self) -> SlashCommandBuilder:
        builder = self.__slash_command_builder_factory(self.__name, self.__description)
        for option in self.__options:
            builder.add_option(transform_option(option))

        if isinstance(self.__permissions, Permission):
            builder.set_default_member_permissions(map_permissions_to_dtos(self.__permissions))

        return builder
