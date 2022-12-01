import pickle as pk
from time import time

import matplotlib as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import complete
from scipy.spatial.distance import pdist

from .base import BaseGraph


class Agglomerative:
    def __init__(self, G: nx.digraph) -> None:
        self.G = G
        self.model = nx.to_pandas_adjacency(G)
        self.matrix = self.model.to_numpy()
        self.clustered_result: np.array
        self.cm: ClusterManager

    def fit(self):
        z = self.matrix
        y = pdist(z, metric="jaccard")
        self.clustered_result = complete(y)
        self.cm = ClusterManager(self.clustered_result, self.model, self.G)


class ClusterManager:
    class Cluster:
        def __init__(self, label: float, clusters: list = [], og=None) -> None:
            self.label = int(label)
            self.map_name = og
            if og:
                self.clusters = [self]
            else:
                self.clusters = []
            for c in clusters:
                self.clusters += c.clusters

        def __hash__(self) -> int:
            return self.label

        def __repr__(self) -> str:
            return str(self.clusters)

    def __init__(self, result: np.array, og: pd.DataFrame, G: nx.digraph) -> None:
        self.result = result
        self.G: nx.DiGraph = G
        self.og = og
        self.init_cn = self.og.columns.to_list()
        self.current_layers = {i: None for i, c in enumerate(self.init_cn)}
        self.clusters = {i: self.Cluster(i, og=c) for i, c in enumerate(self.init_cn)}
        self.layers = self._gen_layers()

    def _gen_layers(self):
        current_label = len(self.init_cn)
        layers = {len(self.init_cn): self.current_layers.copy()}
        for v in self.result:
            c1 = int(v[0])
            c2 = int(v[1])
            del self.current_layers[c1]
            del self.current_layers[c2]
            self.current_layers[current_label] = None
            self.clusters[current_label] = self.Cluster(
                current_label, [self.clusters[c1], self.clusters[c2]]
            )
            layers[len(self.current_layers.keys())] = self.current_layers.copy()
            current_label += 1

        return layers

    def graph(self, n):
        if not self.layers.get(n):
            raise IndexError(f"{n} layer is not exists")

        layer = self.layers.get(n)
        rev_map = {c.map_name: k for k in layer.keys() for c in self.clusters[k].clusters}
        nodes = [n for n in layer.keys()]
        edges = []
        for k in layer.keys():
            for c in self.clusters[k].clusters:
                _out = self.G.out_edges(c.map_name)
                _in = self.G.in_edges(c.map_name)
                for o in _out:
                    edges.append((rev_map[o[0]], rev_map[o[1]]))
                for i in _in:
                    edges.append((rev_map[i[0]], rev_map[i[1]]))

        return BaseGraph.load(nodes, edges)
