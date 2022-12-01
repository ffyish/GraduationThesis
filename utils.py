
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import load_iris

def gen_graph(data) -> nx.DiGraph:
    G = nx.DiGraph(directed=True)
    
    node_ids = dict()
    id_order = 0
    for node in data["Nodes"]:
        if not node_ids.get(node["id"], False):
            node_ids[node["id"]] = id_order
            id_order += 1
            
    # add Node
    nodes = [(node_ids[node["id"]], node["attrs"]) for node in data["Nodes"]]
    G.add_nodes_from(nodes)
    
    # add Edges
    edges = [(
        node_ids[edge["from"]],
        node_ids[edge["to"]],
        edge["attrs"]
        ) for edge in data["Edges"]]
    G.add_edges_from(edges)
    return G

def get_simple_paths(G:nx.DiGraph, source, target)->list:
    return nx.all_simple_paths(G, source, target)


def save_graph(G, to="result.png"):
    nx.draw(G, with_labels=True)
    plt.savefig(to)
    plt.clf()


def graph2AHC(G: nx.DiGraph, linkage="complete") -> AgglomerativeClustering:
    
    X = np.array(G.edges)
    clustering = AgglomerativeClustering(distance_threshold=0, n_clusters=None, linkage=linkage).fit(X)
    return clustering

def plot_dendrogram(model,save_file=False, **kwargs):
    
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)
    if save_file:
        plt.savefig(save_file)
    else:
        plt.show()
    plt.clf()
