from json import load
from typing import Any

import glob
import os

from .types import I18nGroup
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.system import IEnvironment

_ARGUMENTS_SENTINEL: dict[str, Any] = {}
_DEFAULT_LANGUAGE = "default"

@injectable(IStartable)
@injectable(II18nProvider)
class I18nProvider(II18nProvider, IStartable):
    """Implementation of a service used to resolve internationalization keys."""

    def __init__(
        self,
        environment: IEnvironment
    ) -> None:
        super().__init__()
        self.__environment = environment
        self.__languages: dict[str, I18nGroup] = {}

    async def start(self):
        languages: dict[str, I18nGroup] = {}
        i18n_directory = os.path.join(self.__environment.root_path, "resources", "i18n")
        for file_name in glob.glob("*.json", root_dir=i18n_directory):
            file_info = os.path.splitext(file_name)
            name_parts = file_info[0].split("_")
            language = _DEFAULT_LANGUAGE if len(name_parts) < 2 else name_parts[1]
            languages[language] = I18nProvider.__build_map(
                os.path.join(i18n_directory, file_name)
            )
        self.__languages = languages

    async def stop(self):
        pass

    def get(
        self,
        key: str,
        arguments: dict[str, Any] | None = None,
        language: str | None = None
    ) -> str:
        if arguments is None:
            arguments = _ARGUMENTS_SENTINEL
        value = self.__resolve_formatted_key_by_language(key, arguments, language)
        return value if isinstance(value, str) else key

    def get_list(
        self,
        key: str,
        language: str | None = None,
    ) -> tuple[str, ...]:
        value = self.__resolve_formatted_key_by_language(key, _ARGUMENTS_SENTINEL, language)
        return value if isinstance(value, tuple) else ()

    @staticmethod
    def __build_map(file_path: str) -> I18nGroup:
        with open(file_path, encoding="utf-8") as file:
            json = load(file)
            if not isinstance(json, dict):
                raise ValueError(f"The file at the specified path '{file_path}' is not a valid I18N JSON file.")

        root_group = I18nGroup(name="root")
        nodes: list[tuple[I18nGroup, dict[str, Any]]] = [(root_group, json)]
        while nodes:
            parent_group, json = nodes.pop(0)
            for name, value in json.items():
                if isinstance(value, dict):
                    child_group = I18nGroup(name=name)
                    parent_group.value[name] = child_group
                    nodes.append((child_group, value))
                elif isinstance(value, list):
                    parent_group.value[name] = tuple(v for v in value if isinstance(v, str))
                elif isinstance(value, str):
                    parent_group.value[name] = value
        return root_group

    @staticmethod
    def __resolve_key(
        group: I18nGroup,
        subkeys: list[str]
    ) -> str | tuple[str, ...] | None:
        current_group = group
        for subkey in subkeys[:-1]:
            current_group = current_group.value.get(subkey)
            if not isinstance(current_group, I18nGroup):
                return None

        value = current_group.value.get(subkeys[-1])
        return None if isinstance(value, I18nGroup) else value

    @staticmethod
    def __resolve_formatted_key(
        group: I18nGroup,
        subkeys: list[str],
        arguments: dict[str, Any]
    ) -> str | tuple[str, ...] | None:
        value = I18nProvider.__resolve_key(group, subkeys)
        if isinstance(value, tuple):
            return value

        return value.format(**arguments) if value else None

    def __resolve_formatted_key_by_language(
        self,
        key: str,
        arguments: dict[str, Any],
        language: str | None = None
    ) -> str | tuple[str, ...] | None:
        subkeys = key.split(".")
        language_map = self.__languages.get(language) if language else None
        has_checked_default = False
        if not language_map:
            language_map = self.__languages.get(_DEFAULT_LANGUAGE)
            has_checked_default = True
        if not language_map:
            return key
        value = I18nProvider.__resolve_formatted_key(language_map, subkeys, arguments)
        if value is not None:
            return value
        if has_checked_default:
            return key

        language_map = self.__languages.get(_DEFAULT_LANGUAGE)
        value = (
            I18nProvider.__resolve_formatted_key(language_map, subkeys, arguments)
            if language_map else None
        )
        return key if value is None else value
