import os
from json import load

from holobot.sdk.configs import ConfiguratorInterface, TValue
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment

CONFIG_FILE_NAME = "config.json"

@injectable(ConfiguratorInterface)
class Configurator(ConfiguratorInterface):
    def __init__(self, environment: IEnvironment) -> None:
        self.__configs = Configurator.__load_config(environment)

    def get(self, section_name: str, parameter_name: str, default_value: TValue) -> TValue:
        if (env_value := Configurator.__get_env(section_name, parameter_name, default_value)) is not None:
            return env_value
        if not (section := self.__configs.get(section_name)):
            return default_value
        if parameters := section.get("parameters"):
            return parameters.get(parameter_name, default_value)
        return default_value

    @staticmethod
    def __load_config(environment: IEnvironment):
        config_file_path = os.path.join(environment.root_path, CONFIG_FILE_NAME)
        with open(config_file_path) as config_file:
            return load(config_file)

    @staticmethod
    def __get_env(section_name: str, parameter_name: str, default_value: TValue) -> TValue | None:
        if (value := os.environ.get(f"{section_name}-{parameter_name}")) is None:
            return None
        # Because of this check, only the string/bool/int queries are supported, technically.
        match default_value:
            case bool(): return value.upper() == "TRUE"
            case int() | str(): return value
            case list(): return value.split(",")
            case _: return None
