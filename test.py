# TODO Rename all ...Interface classes to I... asap!

from typing import Any, Tuple, Type
from holobot.framework.ioc.graphs import BidirectedGraph
from holobot.framework.ioc.graphs.sorting import TopologicalSorter

import inspect

class IDependency:
    pass

class Service:
    def __init__(self, dependency: IDependency) -> None:
        self.dependency = dependency

class Service2:
    pass

def get_params(type: Type[Any]) -> Tuple[Tuple[str, inspect.Parameter]]:
    constructor = getattr(type, "__init__", None)
    if not constructor or not callable(constructor):
        raise ValueError("Invalid constructor.")
    print(f"Constructor:\n{constructor}") # Output: <function Service.__init__ at 0x...>
    print()

    signature = inspect.signature(constructor)
    for name, descriptor in signature.parameters.items():
        yield (name, descriptor)

print(f"IDependency type: {IDependency}") # Output: <class '__main__.IDependency>
print()

print("Parameters:")
has_dependency = False
for name, descriptor in get_params(IDependency):
    if descriptor.annotation == IDependency:
        has_dependency = True
    print(f"Parameter {name}: {descriptor.annotation}") # Output: name: <class '...'>
print(f"Has IDependency as its dependency: {has_dependency}") # Output: True.
print()

graph: BidirectedGraph[str] = BidirectedGraph()
graph.add_node("Kernel")
graph.add_node("DatabaseManager")
graph.add_node("Migration")
graph.add_node("CryptoUpdater")
graph.add_node("CryptoRepository")
graph.add_node("ViewCryptoCommand")

# Kernel -> DatabaseManager -> Migration
# Kernel -> CryptoUpdater -> CryptoRepository
# Kernel -> ViewCryptoCommand -> CryptoRepository
graph.add_edge("Kernel", "DatabaseManager")
graph.add_edge("DatabaseManager", "Migration")
graph.add_edge("Kernel", "CryptoUpdater")
graph.add_edge("CryptoUpdater", "CryptoRepository")
graph.add_edge("Kernel", "ViewCryptoCommand")
graph.add_edge("ViewCryptoCommand", "CryptoRepository")

for node in TopologicalSorter.sort(graph, "Kernel"):
    print(f"[Sorted] Node: {node}")

stype = Service
inst = stype(*[IDependency()])
print(f"inst.dependency = {inst.dependency}")
