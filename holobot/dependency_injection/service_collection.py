from holobot.dependency_injection.providers.service_provider_base import ServiceProviderBase
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface, T
from holobot.exceptions.aggregate_error import AggregateError
from typing import Dict, List, Type

import inspect

class ServiceCollection(ServiceCollectionInterface):
    def __init__(self):
        self.__providers: List[ServiceProviderBase] = []
        # The list of objects instantiated by a specific interface.
        self.__instances: Dict[Type, List[object]] = {}
        # The interfaces a specific type has already been instantiated by.
        # This exists for performance reasons for quick access in self.__instances.
        self.__interface_map: Dict[Type, List[Type]] = {}
    
    async def close(self):
        print("[ServiceCollection] Closing services...")
        errors = []
        for instances in self.__instances.values():
            for instance in instances:
                close_method = getattr(instance, "close", None)
                if not callable(close_method):
                    continue
                try:
                    if inspect.iscoroutinefunction(close_method):
                        await close_method()
                    else: close_method()
                except BaseException as error:
                    errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        print("[ServiceCollection] Successfully closed services.")

    def add_provider(self, provider: ServiceProviderBase):
        for existing_provider in self.__providers:
            if existing_provider is provider:
                return
        self.__providers.append(provider)
    
    def add_service(self, instance: object, *intfs):
        impl = type(instance)
        if not (interfaces := self.__interface_map.get(impl, None)):
            self.__interface_map[impl] = interfaces = []
        for intf in intfs:
            if not (instances := self.__instances.get(intf, None)):
                self.__instances[intf] = instances = []
            instances.append(instance)
            interfaces.append(intf)

    def get(self, intf: Type[T]) -> T:
        instances = self.__get_or_resolve_instances(intf)
        if len(instances) == 0:
            raise ValueError("None of the providers can provide an instance of the specified type.")
        return instances[0]

    def get_all(self, intf: Type[T]) -> List[T]:
        return self.__get_or_resolve_instances(intf)

    def __get_or_resolve_instances(self, intf: Type[T]) -> List[T]:
        # Determine if we have the instances for this interface.
        instances: List[object] = self.__instances.get(intf, None)
        if instances is None:
            self.__instances[intf] = instances = []
        if len(instances) > 0:
            return instances
        # Since we have no instances yet, create all of them.
        return self.__resolve_instances(intf)
    
    def __resolve_instances(self, intf: Type[T]) -> List[T]:
        instances: List[object] = []
        # Ask all providers to have all the exports.
        for provider in self.__providers:
            if not provider.knows(intf):
                continue
            # Get all the implementations for this particular interface.
            impls = provider.get_impls(intf)
            # Determine if there are instances for each implementation.
            for impl in impls:
                if not (intfs := self.__interface_map.get(impl, None)):
                    self.__interface_map[impl] = intfs = list()
                if len(intfs) > 0:
                    # Since we have the instance instantiated for at least
                    # one interface already, just take the first one.
                    instances.append(self.__get_instance_for(intfs[0], impl))
                    print(f"[ServiceCollection] Found existing instance of {impl} for {intf}.")
                    continue
                # The first instance needs to be created.
                instance = impl(self)
                self.__instances[intf] = [instance]
                intfs.append(intf)
                instances.append(instance)
                print(f"[ServiceCollection] Resolved a new instance of {impl} for {intf}.")
        return instances
    
    def __get_instance_for(self, intf: Type, impl: Type) -> object:
        for instance in self.__instances[intf]:
            if isinstance(instance, impl):
                return instance
        raise ValueError("Expected a specific instance to exist for a specific interface and implementation.")
