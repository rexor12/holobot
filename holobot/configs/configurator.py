from holobot.logging.log_interface import LogInterface
from holobot.configs.configurator_interface import ConfiguratorInterface, T
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from json import load
from os import environ
from typing import Final, Optional

CONFIG_FILE_PATH: Final[str] = ".\\config.json"

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
        # Because of this check, only the string queries are supported, technically.
        if not isinstance(default_value, str):
            return None
        return environ.get(f"{section_name}/{parameter_name}", None)
