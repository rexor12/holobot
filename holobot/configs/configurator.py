from holobot.logging.log_interface import LogInterface
from holobot.configs.configurator_interface import ConfiguratorInterface, T
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from json import load
from typing import Final, Optional

import os

# TODO Move this to a new service that provides environment related information.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE_PATH: Final[str] = os.path.join(BASE_DIR, "config.json")

class Configurator(ConfiguratorInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        with open(CONFIG_FILE_PATH) as config_file:
            self.__configs = load(config_file)
        service_collection.get(LogInterface).info(f"[Configurator] Loaded configuration. {{ SectionCount = {len(self.__configs)} }}")

    def get(self, section_name: str, parameter_name: str, default_value: T) -> T:
        # TODO Temporary change to support Heroku's way of configuration.
        if (env_value := Configurator.__get_env(section_name, parameter_name, default_value)) is not None:
            return env_value
        if not (section := self.__configs.get(section_name, None)):
            return default_value
        if not (parameters := section.get("parameters", None)):
            return default_value
        return parameters.get(parameter_name, default_value)
    
    @staticmethod
    def __get_env(section_name: str, parameter_name: str, default_value: T) -> Optional[T]:
        if (value := os.environ.get(f"{section_name}-{parameter_name}", None)) is None:
            return None
        # Because of this check, only the string/bool/int queries are supported, technically.
        if type(default_value) is str:
            return value
        elif type(default_value) is bool:
            return value.upper() == "TRUE"
        elif type(default_value) is int:
            return int(value)
        return None
