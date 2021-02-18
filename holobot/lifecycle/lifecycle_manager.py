from holobot.dependency_injection.service_collection import ServiceCollectionInterface
from holobot.exceptions.aggregate_error import AggregateError
from holobot.lifecycle.lifecycle_manager_interface import LifecycleManagerInterface
from holobot.lifecycle.startable_interface import StartableInterface
from typing import List

class LifecycleManager(LifecycleManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__startables: List[StartableInterface] = service_collection.get_all(StartableInterface)
    
    async def start_all(self):
        errors = []
        for startable in self.__startables:
            try:
                await startable.start()
            except BaseException as error:
                errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        print("[LifecycleManager] Successfully started all services.")
    
    async def stop_all(self):
        errors = []
        for startable in self.__startables:
            try:
                await startable.stop()
            except BaseException as error:
                errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        print("[LifecycleManager] Successfully stopped all services.")