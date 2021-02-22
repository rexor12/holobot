from holobot.logging.log_interface import LogInterface
from holobot.configs.configurator_interface import ConfiguratorInterface, T
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from json import load
from typing import Final

CONFIG_FILE_PATH: Final[str] = ".\\config.json"

class Configurator(ConfiguratorInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        with open(CONFIG_FILE_PATH) as config_file:
            self.__configs = load(config_file)
        service_collection.get(LogInterface).info(f"[Configurator] Loaded configuration. {{ SectionCount = {len(self.__configs)} }}")

    def get(self, section_name: str, parameter_name: str, default_value: T) -> T:
        if not (section := self.__configs.get(section_name, None)):
            return default_value
        if not (parameters := section.get("parameters", None)):
            return default_value
        return parameters.get(parameter_name, default_value)
