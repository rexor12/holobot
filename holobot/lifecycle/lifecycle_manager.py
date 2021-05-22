from .lifecycle_manager_interface import LifecycleManagerInterface
from .startable_interface import StartableInterface
from ..dependency_injection import injectable, ServiceCollectionInterface
from ..exceptions import AggregateError
from ..logging import LogInterface
from typing import List

@injectable(LifecycleManagerInterface)
class LifecycleManager(LifecycleManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__startables: List[StartableInterface] = service_collection.get_all(StartableInterface)
        self.__log = service_collection.get(LogInterface)
    
    async def start_all(self):
        errors = []
        for startable in self.__startables:
            try:
                await startable.start()
            except BaseException as error:
                errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        self.__log.info("[LifecycleManager] Successfully started all services.")
    
    async def stop_all(self):
        errors = []
        for startable in self.__startables:
            try:
                await startable.stop()
            except BaseException as error:
                errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        self.__log.info("[LifecycleManager] Successfully stopped all services.")