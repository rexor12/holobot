from holobot.sdk.configs import ConfiguratorInterface, TValue
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import EnvironmentInterface
from json import load
from typing import Optional

import os

CONFIG_FILE_NAME = "config.json"

@injectable(ConfiguratorInterface)
class Configurator(ConfiguratorInterface):
    def __init__(self, environment: EnvironmentInterface) -> None:
        self.__configs = Configurator.__load_config(environment)

    def get(self, section_name: str, parameter_name: str, default_value: TValue) -> TValue:
        # TODO Temporary change to support Heroku's way of configuration.
        if (env_value := Configurator.__get_env(section_name, parameter_name, default_value)) is not None:
            return env_value
        if not (section := self.__configs.get(section_name, None)):
            return default_value
        if not (parameters := section.get("parameters", None)):
            return default_value
        return parameters.get(parameter_name, default_value)

    @staticmethod
    def __load_config(environment: EnvironmentInterface):
        config_file_path = os.path.join(environment.root_path, CONFIG_FILE_NAME)
        with open(config_file_path) as config_file:
            return load(config_file)

    @staticmethod
    def __get_env(section_name: str, parameter_name: str, default_value: TValue) -> Optional[TValue]:
        if (value := os.environ.get(f"{section_name}-{parameter_name}", None)) is None:
            return None
        # Because of this check, only the string/bool/int queries are supported, technically.
        if type(default_value) is str:
            return value
        elif type(default_value) is bool:
            return value.upper() == "TRUE"
        elif type(default_value) is int:
            return int(value)
        elif type(default_value) is list:
            return value.split(",")
        return None
