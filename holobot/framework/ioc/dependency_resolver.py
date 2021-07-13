from .graphs import BidirectedGraph
from .graphs.sorting import TopologicalSorter
from holobot.sdk.ioc.models import ExportMetadata
from holobot.sdk.utils import get_or_add
from typing import Any, Dict, Generator, List, Set, Tuple, Type, TypeVar, get_args

import inspect, logging

TService = TypeVar("TService")

class DependencyResolver:
	def __init__(self, exports: Tuple[ExportMetadata, ...]) -> None:
		self.__log = logging.Logger("DependencyResolver")
		self.__intf_to_impl_map: Dict[Type[Any], Set[Type[Any]]] = {}
		self.__impl_to_intf_map: Dict[Type[Any], Set[Type[Any]]] = {}
		self.__instances_by_intf: Dict[Type[Any], List[Any]] = {}
		self.__build_export_maps(exports)
	
	def resolve(self, type: Type[TService]) -> TService:
		dependency_graph = self.__build_dependeny_graph_for(type)
		for service_type in TopologicalSorter.sort(dependency_graph, type):
			self.__log.debug(f"Resolving service... {{ Type = {service_type.__name__} }}")
			self.__resolve_service(service_type)
			self.__log.debug(f"Resolved service. {{ Type = {service_type.__name__} }}")
		return self.__create_instance(type)

	# Idea from: https://github.com/agronholm/typeguard
	@staticmethod
	def __unpack_dependent_intf(type: Type[Any]) -> Tuple[Type[Any], bool]:
		print(f"Unpacking interface... {{ Type = {type} }}")
		if (origin := getattr(type, "__origin__", None)) is not None:
			if origin != tuple:
				raise ValueError(f"Expected a tuple, but got {origin.__name__}.")
			args = get_args(type)
			if len(args) != 2 or args[-1] != Ellipsis:
				raise ValueError("Expected a tuple with two arguments, the second being an ellipsis.")
			return (args[0], True)
		return (type, False)
	
	def __build_export_maps(self, exports: Tuple[ExportMetadata, ...]) -> None:
		for export in exports:
			impl_list: Set[Type[Any]] = get_or_add(self.__intf_to_impl_map, export.contract_type, set())
			impl_list.add(export.export_type)
			intf_list: Set[Type[Any]] = get_or_add(self.__impl_to_intf_map, export.export_type, set())
			intf_list.add(export.contract_type)

	def __build_dependeny_graph_for(self, type: Type[Any]) -> BidirectedGraph[Type[Any]]:
		dependency_graph: BidirectedGraph[Type[Any]] = BidirectedGraph()
		resolvable_impls: List[Type[Any]] = [type]
		while len(resolvable_impls) > 0:
			dependee_impl = resolvable_impls.pop()
			if not dependency_graph.try_add_node(dependee_impl):
				# This type's dependency chain has already been mapped.
				continue

			self.__log.debug(f"Gathering dependent interfaces... {{ Dependee = {dependee_impl.__name__} }}")
			for dependent_intf, is_multi in self.__get_dependent_intfs(dependee_impl):
				self.__log.debug(f"Found dependent interface. {{ Dependee = {dependee_impl.__name__}, Dependent = {dependent_intf.__name__}, IsMulti = {is_multi} }}")
				if len(dependent_impls := self.__intf_to_impl_map.get(dependent_intf, [])) == 0 and not is_multi:
					raise ValueError(f"Cannot satisfy dependency. {{ Dependee = {dependee_impl.__name__}, Dependent = {dependent_intf.__name__} }}")

				for dependent_impl in dependent_impls:
					dependency_graph.try_add_node(dependee_impl)
					dependency_graph.add_edge(dependee_impl, dependent_impl)
					resolvable_impls.append(dependent_impl)
					self.__log.debug(f"Identified dependent implementation. {{ Dependee = {dependee_impl.__name__}, Dependent = {dependent_impl.__name__} }}")

		return dependency_graph

	def __get_dependent_intfs(self, service_type: Type[Any]) -> Generator[Tuple[Type[Any], bool], None, None]:
		constructor = getattr(service_type, "__init__", None)
		if not constructor or not callable(constructor):
			raise ValueError("Invalid constructor.")
		signature = inspect.signature(constructor)
		for name, descriptor in signature.parameters.items():
			if name in ("self", "args", "kwargs"):
				continue
			if descriptor.annotation == inspect.Parameter.empty:
				raise ValueError("Missing annotation.")
			yield DependencyResolver.__unpack_dependent_intf(descriptor.annotation)

	def __resolve_service(self, service_type: Type[TService]) -> TService:
		export_intfs = list(self.__impl_to_intf_map[service_type])
		# Check one of the interfaces to see if there is an instance of this service yet.
		# The interface doesn't matter, because the same instance is associated to
		# all of its interfaces.
		if (instances := self.__instances_by_intf.get(export_intfs[0], None)) is not None:
			for instance in instances:
				if type(instance) == service_type:
					return instance

		instance = self.__create_instance(service_type)
		for intf in self.__impl_to_intf_map[service_type]:
			instances = get_or_add(self.__instances_by_intf, intf, [])
			instances.append(instance)
		
		return instance
	
	def __create_instance(self, service_type: Type[TService]) -> TService:
		dependent_intfs = self.__get_dependent_intfs(service_type)
		dependent_impls = []
		for dependent_intf, is_multi in dependent_intfs:
			instances = self.__instances_by_intf.get(dependent_intf, [])
			if is_multi:
				dependent_impls.append(tuple(instances))
			elif len(instances) > 0:
				dependent_impls.append(instances[0])
			else: raise ValueError(f"Cannot satisfy dependency of '{service_type}' on '{dependent_intf}'.")
		
		return service_type(*dependent_impls)
