import os
from json import load
from typing import Any, cast

from holobot.sdk.configs import IConfigurator, TValue
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.serialization.json_serializer import deserialize
from holobot.sdk.system import IEnvironment

_CONFIG_FILE_NAME = "config.json"

@injectable(IConfigurator)
class Configurator(IConfigurator):
    def __init__(self, environment: IEnvironment) -> None:
        self.__configs = Configurator.__load_config(environment)

    def get(self, section_name: str, parameter_name: str, default_value: TValue) -> TValue:
        if (value := Configurator.__try_get_from_env(section_name, parameter_name, default_value)) is not None:
            return value

        if not (section := self.__configs.get(section_name)):
            return default_value
        if not isinstance(section, dict) or not (parameters := section.get("parameters")):
            return default_value
        if not isinstance(parameters, dict):
            return default_value
        if (parameter := parameters.get(parameter_name)) is not None:
            return Configurator.__get_parameter_value(parameter, default_value)
        return default_value

    @staticmethod
    def __load_config(environment: IEnvironment) -> dict[str, Any]:
        config_file_path = os.path.join(environment.root_path, _CONFIG_FILE_NAME)
        with open(config_file_path) as config_file:
            return load(config_file)

    @staticmethod
    def __try_get_from_env(
        section_name: str,
        parameter_name: str,
        default_value: TValue
    ) -> TValue | None:
        if (value := os.environ.get(f"{section_name}-{parameter_name}", None)) is not None:
            if isinstance(value, type(default_value)):
                return value
            return deserialize(type(default_value), f"\"{value}\"")

    @staticmethod
    def __get_parameter_value(parameter_value: Any, default_value: TValue) -> TValue:
        if type(default_value) is str and isinstance(parameter_value, str):
            return cast(TValue, parameter_value)
        elif type(default_value) is bool:
            if isinstance(parameter_value, bool):
                return cast(TValue, parameter_value)
            elif isinstance(parameter_value, (str, int)):
                return cast(TValue, bool(parameter_value))
        elif type(default_value) is int:
            if isinstance(parameter_value, int):
                return cast(TValue, parameter_value)
            elif isinstance(parameter_value, str):
                return cast(TValue, int(parameter_value))
        elif type(default_value) is list and isinstance(parameter_value, list):
            return parameter_value.split(",") # type: ignore
        return default_value
