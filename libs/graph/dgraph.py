from collections import defaultdict

from ujson import load

from .base import BaseGraph


class DynamicGraph(BaseGraph):
    @classmethod
    def load_json(cls, f, attrs=False) -> "BaseGraph":
        data = load(f)

        nodes = data["Nodes"]
        edges = data["Edges"]

        node_l = {}
        hashed_edges = defaultdict(list)

        for edge in edges:
            is_dynamic = edge["attrs"]["isDynamic"]
            pos = edge["attrs"]["pos"]

            if not is_dynamic:
                edge_hash = "#"
            else:
                edge_hash = hash(f'{pos["name"]}:{pos["line"]}:{pos["column"]}')

            edge["hash"] = edge_hash

        for edge in edges:
            hashed_edges[edge["hash"]].append(edge)
