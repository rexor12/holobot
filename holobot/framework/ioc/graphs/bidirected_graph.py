from .edge import Edge
from .graph import Graph
from .tnode import TNode
from typing import Generator

class BidirectedGraph(Graph[TNode]):
    def __init__(self) -> None:
        super().__init__()

    def get_out_edges(self, node: TNode) -> Generator[Edge[TNode], None, None]:
        if not node in self:
            raise ValueError(f"The node '{node}' is not in the graph.")
        
        for edge in self.edges:
            if edge.source == node:
                yield edge
    
    def _is_same_edge(self, existing_edge: Edge, new_edge: Edge) -> bool:
        return existing_edge == new_edge
