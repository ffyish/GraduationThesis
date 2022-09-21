


from copy import deepcopy
from functools import cache
from typing import Set

import networkx as nx
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from memory_profiler import profile
from networkx.drawing.nx_pydot import graphviz_layout, to_pydot
from tabulate import tabulate

COLUMN = 1
ROW = 0

class AgglomerativeClustering:
    def __init__(self, model:pd.DataFrame) -> None:
        self.model = model
        def get_dist(base:np.array):
            def _get_dist(target:np.array):
                return 1 - (np.logical_and(base, target).sum() / np.logical_or(base, target).sum())
            
            return _get_dist
        
        matrix_ = model.to_numpy()
        dist_matrix = []
        for idx, row in enumerate(matrix_):
            res = np.apply_along_axis(get_dist(row),COLUMN,matrix_)
            res[idx] = 100
            dist_matrix.append(res)
        
        self.dist_matrix = np.array(dist_matrix)
        self.init_clusters = [Cluster(paths=set([i]), label=f"c{i+1}") for i in range(len(self.dist_matrix))]
        
    @cache
    def _max_dist(self, c1, c2):
        path1 = c1.path
        path2 = c2.path
        max_d = 0
        for p1 in path1:
            for p2 in path2:
                if p1 != p2 and self.dist_matrix[p1, p2] > max_d:
                    max_d = self.dist_matrix[p1, p2]
                    
        return max_d
                    
    
    def create(self):
        clusters:list = deepcopy(self.init_clusters)
        cluster_matrix = deepcopy(self.dist_matrix)
        cluster_graph = dict()
        # print(cluster_matrix)
        
        
        clst_idx = len(clusters)
        while len(clusters) > 1:
            min_ = 1000
            target_ = None
            for i, row in enumerate(cluster_matrix):
                val = np.amin(row)
                if np.amin(row) < min_:
                    target_ = [i, np.argmin(row)]
                    min_ = val
            
            cluster_label = f"c{clst_idx+1}"
            new_cluster = clusters[target_[0]] + clusters[target_[1]]
            cluster_graph[cluster_label] = [clusters[target_[0]].label, clusters[target_[1]].label]
            new_cluster.set_label(cluster_label)

            target_.sort()
            clusters.pop(target_[0])
            clusters.pop(target_[1]-1)
            
            clusters.append(new_cluster)
            
            cluster_matrix = np.delete(cluster_matrix, (target_[0], target_[1]), ROW)
            cluster_matrix = np.delete(cluster_matrix, (target_[0], target_[1]), COLUMN)
            
            
            # generate new row, col
            new_values = []
            for idx, cluster in enumerate(clusters):
                if idx == (len(clusters) - 1):
                    new_values.append(100)
                else:
                    new_values.append(self._max_dist(new_cluster, cluster))
                    
            new_values = np.array([new_values])
            
            row_n = cluster_matrix.shape[0]
            cluster_matrix = np.append(cluster_matrix, [new_values[0,:-1]], ROW)
            cluster_matrix = np.append(cluster_matrix, new_values.T, COLUMN)
            clst_idx += 1
        
        return DendGraph(cluster_graph).reverse()
            

class DendGraph(nx.DiGraph):
    def show(self):
        pos = graphviz_layout(self, "dot")
        flipped_pos = {node: (x,-y) for (node, (x,y)) in pos.items()}
        plt.clf()
        nx.draw(self, flipped_pos, with_labels=True, node_color="tab:red", alpha=0.9,font_color="whitesmoke", font_size=10)
        plt.show()
        # p = to_pydot(self)
        # p.write_png("dendrogram.png")
            
                    
                
                
            
        
                
            
class Cluster:
    def __init__(self,label:str=None, childs:list = [] ,paths:set = set()) -> None:
        self.paths = paths
        self.childs = childs
        self.label = label
    
    @property
    @cache
    def path(self):
        path = self.paths
        for child in self.childs:
            path |= child.path
        return path
    
    def set_label(self, name):
        self.label = name
        
    def __add__(self, o:"Cluster") -> "Cluster":
        if isinstance(self, Cluster):
            return Cluster(childs=[self, o])
        else:
            raise "can not add"
        
    
    def __repr__(self) -> str:
        return f"<Cluster {str(self.label)}>"
