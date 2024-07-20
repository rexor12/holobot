import glob
import os
import random
from collections.abc import Iterable
from json import load
from typing import Any

from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.system import IEnvironment
from .types import I18nGroup

_ARGUMENTS_SENTINEL: dict[str, Any] = {}
_DEFAULT_LANGUAGE = "default"

@injectable(IStartable)
@injectable(II18nProvider)
class I18nProvider(II18nProvider, IStartable):
    """Implementation of a service used to resolve internationalization keys."""

    def __init__(
        self,
        environment: IEnvironment,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__environment = environment
        self.__logger = logger_factory.create(I18nProvider)
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
        try:
            value = self.__resolve_key(key, arguments, language)
            return value if isinstance(value, str) else key
        except Exception as error:
            self.__logger.error(
                "Failed to resolve I18N key",
                error,
                key=key
            )
            return key

    def get_list(
        self,
        key: str,
        language: str | None = None,
    ) -> tuple[str, ...]:
        try:
            value = self.__resolve_key(key, _ARGUMENTS_SENTINEL, language)
            return value if isinstance(value, tuple) else ()
        except Exception as error:
            self.__logger.error(
                "Failed to resolve list-type I18N key",
                error,
                key=key
            )
            return ()

    def get_list_item(
        self,
        key: str,
        item_index: int,
        arguments: dict[str, Any] | None = None,
        language: str | None = None
    ) -> str:
        if item_index < 0:
            return key
        if arguments is None:
            arguments = _ARGUMENTS_SENTINEL

        try:
            value = self.__get_value_by_key(key, language)
            if value is None or not isinstance(value, tuple) or len(value) <= item_index:
                return key

            return value[item_index].format(**arguments)
        except Exception as error:
            self.__logger.error(
                "Failed to resolve list item-type I18N key",
                error,
                key=key,
                item_index=item_index
            )
            return key

    def get_list_items(
        self,
        key: str,
        item_arguments: Iterable[dict[str, Any]],
        language: str | None = None
    ) -> tuple[str, ...]:
        try:
            value = self.__get_value_by_key(key, language)
            if value is None or isinstance(value, tuple):
                return ()

            return tuple(value.format(**arguments) for arguments in item_arguments)
        except Exception as error:
            self.__logger.error(
                "Failed to resolve list item-type I18N key",
                error,
                key=key
            )
            return ()

    def get_random_list_item(
        self,
        key: str,
        language: str | None = None
    ) -> str:
        try:
            value = self.__resolve_key(key, _ARGUMENTS_SENTINEL, language)
            if not isinstance(value, tuple):
                return key

            return random.choice(value)
        except Exception as error:
            self.__logger.error(
                "Failed to resolve list-type I18N key",
                error,
                key=key
            )
            return key

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
    def __find_value_in_group(
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

    def __get_value_by_key(
        self,
        key: str,
        language: str | None
    ) -> str | tuple[str, ...] | None:
        subkeys = key.split(".")
        language_map = self.__languages.get(language) if language else None
        has_checked_default = False
        if not language_map:
            language_map = self.__languages.get(_DEFAULT_LANGUAGE)
            has_checked_default = True
        if not language_map:
            return None
        value = I18nProvider.__find_value_in_group(language_map, subkeys)
        if value is not None:
            return value
        if has_checked_default:
            return None

        language_map = self.__languages.get(_DEFAULT_LANGUAGE)
        return (
            I18nProvider.__find_value_in_group(language_map, subkeys)
            if language_map else None
        )

    def __resolve_key(
        self,
        key: str,
        arguments: dict[str, Any],
        language: str | None = None
    ) -> str | tuple[str, ...] | None:
        value = self.__get_value_by_key(key, language)
        if value is None:
            return key

        return value if isinstance(value, tuple) else value.format(**arguments)
