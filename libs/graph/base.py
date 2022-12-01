import networkx as nx
from ujson import load


class BaseGraph(nx.DiGraph):
    @classmethod
    def load_json(cls, f, attrs=False) -> "BaseGraph":
        G = cls(directed=True)
        data = load(f)
        if not attrs:
            nodes = [node["id"] for node in data["Nodes"]]
        else:
            nodes = [(node["id"], node["attrs"]) for node in data["Nodes"]]

        G.add_nodes_from(nodes)

        # add Edges

        if not attrs:
            edges = [(edge["from"], edge["to"]) for edge in data["Edges"]]
        else:
            edges = [(edge["from"], edge["to"], edge["attrs"]) for edge in data["Edges"]]
        G.add_edges_from(edges)

        def relabel(label: str):
            if label.startswith("("):
                return f"({label.split('/')[-1]}"
            else:
                return label.split("/")[-1]

        if attrs:
            new_G = nx.relabel_nodes(G, {node: relabel(node) for node in G.nodes()})
            return new_G
        else:
            return G

    @classmethod
    def load(cls, nodes, edges) -> "BaseGraph":
        G = cls(directed=True)
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        return G
