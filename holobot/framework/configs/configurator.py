import os
import re
from json import load
from queue import Queue
from typing import Any, cast

from holobot.sdk.configs import IConfigurator, TValue
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment
from holobot.sdk.utils.dict_utils import merge

@injectable(IConfigurator)
class Configurator(IConfigurator):
    _MAIN_CONFIG_FILE_NAME = "config.json"
    _ENV_CONFIG_FILE_NAME = "config.{env}.json"
    _ENV_VAR_REGEX = re.compile(r"^__(?P<name>\w+)__$")

    @property
    def effective_config(self) -> dict[str, Any]:
        return self.__configs

    def __init__(self, environment: IEnvironment) -> None:
        self.__configs = Configurator.__load_config(environment)

    def get_parameter(
        self,
        section_name: str | tuple[str, ...],
        parameter_name: str,
        default_value: TValue
    ) -> TValue:
        if not section_name:
            return default_value

        if isinstance(section_name, str):
            section_name = (section_name, parameter_name)
        else:
            section_name += (parameter_name,)

        section_or_parameter = self.effective_config.get(section_name[0])
        for subsection_name in section_name[1:]:
            if not isinstance(section_or_parameter, dict):
                return default_value
            section_or_parameter = section_or_parameter.get(subsection_name)

        if section_or_parameter is None or isinstance(section_or_parameter, dict):
            return default_value

        if isinstance(section_or_parameter, list):
            if isinstance(default_value, list):
                return cast(TValue, section_or_parameter)
            else:
                return default_value

        try:
            return type(default_value)(cast(Any, section_or_parameter))
        except TypeError:
            return default_value

    @staticmethod
    def __load_config(environment: IEnvironment) -> dict[str, Any]:
        config_file_paths = [
            os.path.join(environment.root_path, Configurator._MAIN_CONFIG_FILE_NAME)
        ]
        if (env := os.environ.get("HOLO_ENVIRONMENT", None)):
            config_file_paths.append(
                os.path.join(
                    environment.root_path,
                    Configurator._ENV_CONFIG_FILE_NAME.format(env=env)
                )
            )

        effective_config = dict[str, Any]()
        for config_file_path in config_file_paths:
            if os.path.exists(config_file_path) and os.path.isfile(config_file_path):
                with open(config_file_path) as config_file:
                    merge(effective_config, load(config_file))

        Configurator.__resolve_environment_variables(effective_config)

        return effective_config

    @staticmethod
    def __resolve_environment_variables(effective_config: dict[str, Any]) -> None:
        nodes = Queue[dict[str, Any]]()
        nodes.put(effective_config)
        while not nodes.empty():
            node = nodes.get()
            for key, value in node.items():
                if isinstance(value, dict):
                    nodes.put(value)
                elif (
                    isinstance(value, str)
                    and (env_var := Configurator._ENV_VAR_REGEX.match(value))
                ):
                    node[key] = os.environ.get(env_var["name"], value)
