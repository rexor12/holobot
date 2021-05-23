from .environment_interface import EnvironmentInterface
from .models import Version
from ..dependency_injection import injectable, ServiceCollectionInterface

@injectable(EnvironmentInterface)
class Environment(EnvironmentInterface):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()
        # NOTE: This version number is automatically updated on build by the script assign_version.yml.
        self.version = Version(2, 0, 0, 126)
