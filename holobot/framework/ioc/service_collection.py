from holobot.sdk.exceptions import AggregateError
from holobot.sdk.ioc import DeferredService, ServiceCollectionInterface, TService
from holobot.sdk.ioc.providers import ServiceProviderBase
from threading import RLock
from typing import Any, Dict, List, Optional, Set, Tuple, Type

import inspect

class ServiceCollection(ServiceCollectionInterface):
    def __init__(self):
        self.__lock: RLock = RLock()
        self.__providers: List[ServiceProviderBase] = []
        # The list of objects instantiated by a specific interface.
        self.__instances: Dict[Type, List[Any]] = {}
        # The interfaces a specific type has already been instantiated by.
        # This exists for performance reasons for quick access in self.__instances.
        self.__interface_map: Dict[Type, List[Type]] = {}
        # Used for finding loops in the dependency graph.
        self.__types_under_initialization: Set[Type[Any]] = set()
    
    # TODO Use the LifecycleManager with the StoppableInterface instead.
    # This is a leftover from the early development when the ServiceCollection
    # still didn't support exports by multiple interfaces.
    async def close(self):
        print("[ServiceCollection] Closing services...")
        errors: List[Exception] = []
        for instances in self.__instances.values():
            for instance in instances:
                close_method = getattr(instance, "close", None)
                if not callable(close_method):
                    continue
                try:
                    if inspect.iscoroutinefunction(close_method):
                        await close_method()
                    else: close_method()
                except Exception as error:
                    errors.append(error)
        if len(errors) > 0:
            raise AggregateError(errors)
        print("[ServiceCollection] Successfully closed services.")

    def add_provider(self, provider: ServiceProviderBase):
        with self.__lock:
            for existing_provider in self.__providers:
                if existing_provider is provider:
                    return
            self.__providers.append(provider)
    
    # NOTE: Dependencies won't be re-resolved when a new service is added.
    def add_service(self, instance: object, *intfs):
        with self.__lock:
            impl = type(instance)
            if not (interfaces := self.__interface_map.get(impl, None)):
                self.__interface_map[impl] = interfaces = []
            for intf in intfs:
                if not (instances := self.__instances.get(intf, None)):
                    self.__instances[intf] = instances = []
                instances.append(instance)
                interfaces.append(intf)

    def get(self, intf: Type[TService]) -> TService:
        instances = self.__get_or_resolve_instances(intf)
        if len(instances) == 0:
            raise ValueError(f"None of the providers can provide an instance of type '{intf}'.")
        return instances[0]

    def get_all(self, intf: Type[TService]) -> Tuple[TService, ...]:
        return self.__get_or_resolve_instances(intf)
    
    def get_deferred(self, type: Type[TService]) -> DeferredService[TService]:
        return DeferredService(lambda: self.get(type))

    def __get_or_resolve_instances(self, intf: Type[TService]) -> Tuple[TService, ...]:
        with self.__lock:
            # If the instances exist already, we just return them.
            instances: Optional[List[TService]] = self.__instances.get(intf, None)
            if instances is not None and len(instances) > 0:
                return tuple(instances)
            # Otherwise, we need to resolve the instances.
            self.__instances[intf] = instances = self.__resolve_instances(intf)
            return tuple(instances)
    
    def __resolve_instances(self, intf: Type[TService]) -> List[TService]:
        instances: List[Any] = []
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
                    continue
                # The first instance needs to be created.
                if impl in self.__types_under_initialization:
                    raise ValueError(f"The type '{impl}' is already being initialized. This is a loop in the dependency graph.")
                self.__types_under_initialization.add(impl)
                instance = impl(self)
                self.__types_under_initialization.remove(impl)
                self.__instances[intf] = [instance]
                intfs.append(intf)
                instances.append(instance)
        return instances
    
    def __get_instance_for(self, intf: Type, impl: Type) -> object:
        for instance in self.__instances[intf]:
            if isinstance(instance, impl):
                return instance
        raise ValueError("Expected an instance to exist for a specific interface and implementation.")
