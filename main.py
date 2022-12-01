import json
import pickle as pk
from timeit import timeit

import matplotlib.pyplot as plt
import networkx as nx

from libs.graph.base import BaseGraph
from libs.graph.digraph import ClusterManager

ff = open("sample.json")
# gd = json.load(ff)
# od = {n["id"]: f"f{i+1}" for i, n in enumerate(gd["Nodes"])}
# nodes = [f"f{i+1}" for i, n in enumerate(gd["Nodes"])]
# edges = [(od[e["from"]], od[e["to"]]) for e in gd["Edges"]]
# # edges += [("f7", "f8")]
# G = BaseGraph.load(nodes, edges)
# print(nx.to_pandas_adjacency(G))
# nx.draw_circular(G, with_labels=True)
# plt.show()

f = open("rclone.json", "r")
# pd.set_option('display.max_columns', None)
print("START LOADING....")

result = pk.load(open("cluster_sample.pk", "rb"))
G = BaseGraph.load_json(f, attrs=False)

cycles = nx.simple_cycles(G)
for c in cycles:
    print(c)


# model = nx.to_pandas_adjacency(G)
# cm = ClusterManager(result, model, G)
# gg = cm.graph(50)
# options = {"with_labels": False, "node_size": 60}
# nx.draw_kamada_kawai(gg, **options)
# plt.show()
