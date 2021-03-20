from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.system.environment_interface import EnvironmentInterface
from holobot.system.models.version import Version

class Environment(EnvironmentInterface):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()
        # NOTE: This version number is automatically updated on build by the script assign_version.yml.
        self.version = Version(1, 0, 0, 0)
