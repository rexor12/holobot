from .. import BidirectedGraph, TNode
from ..exceptions import CyclicGraphError, DisconnectedSubGraphError
from holobot.sdk.exceptions import ArgumentError
from typing import List, Set, Tuple

class TopologicalSorter:
    @staticmethod
    def sort(graph: BidirectedGraph[TNode], start_node: TNode) -> Tuple[TNode, ...]:
        if not start_node in graph:
            raise ArgumentError("start_node", f"The start node '{start_node}' is not in the graph.")
        
        visited_nodes: Set[TNode] = set()
        unvisited_nodes: Set[TNode] = graph.nodes
        sorted_nodes: List[TNode] = []
        TopologicalSorter.__visit(graph, start_node, visited_nodes, set(), sorted_nodes)
        if not visited_nodes == unvisited_nodes:
            raise DisconnectedSubGraphError(tuple(str(node) for node in unvisited_nodes))
        return tuple(sorted_nodes)
    
    @staticmethod
    def __visit(graph: BidirectedGraph[TNode], node: TNode, visited_nodes: Set[TNode], currently_visiting: Set[TNode], sorted_nodes: List[TNode]) -> None:
        if node in visited_nodes:
            return
        if node in currently_visiting:
            raise CyclicGraphError(currently_visiting, "A directed acyclic graph (DAG) is expected.")
        
        currently_visiting.add(node)
        for out_node in set(edge.target for edge in graph.get_out_edges(node)):
            TopologicalSorter.__visit(graph, out_node, visited_nodes, currently_visiting, sorted_nodes)
        currently_visiting.remove(node)

        visited_nodes.add(node)
        sorted_nodes.append(node)
