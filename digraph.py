
import re
from collections import defaultdict
from copy import deepcopy
from importlib.metadata import entry_points
from itertools import cycle
from pprint import pp

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from ujson import load


class OHCGraph(nx.DiGraph):
    @classmethod
    def load_json(cls, f, as_id=True) -> "OHCGraph":
        G = cls(directed=True)
        data = load(f)
        node_ids = dict()
        if as_id:
            id_order = 0
            for node in data["Nodes"]:
                if not node_ids.get(node["id"], False):
                    node_ids[node["id"]] = id_order
                    id_order += 1
                    
            # add Node
            nodes = [(node_ids[node["id"]], node["attrs"]) for node in data["Nodes"]]
        else:
            nodes = [(node["id"], node["attrs"]) for node in data["Nodes"]]
        # else:
        #     def sum_label(lb:str):
        #         simple_lb = ""
        #         if lb.startswith("("):
        #             _lb:str = re.findall("\((.*?)\)", lb)[0]
                    
        #             if _lb.startswith("*"):
        #                 simple_lb = f'(*{ _lb.split("/")[-1]}).{lb.split(".")[-1]}'
        #             else:
        #                 simple_lb = f'({ _lb.split("/")[-1]}).{lb.split(".")[-1]}'
        #         else:
        #             simple_lb = lb.split("/")[-1]
                        
        #         return simple_lb
        
            
        G.add_nodes_from(nodes)
        
        
        # add Edges
        
        if as_id:
            edges = [(
                node_ids[edge["from"]],
                node_ids[edge["to"]],
                edge["attrs"]
                ) for edge in data["Edges"]]
        else:
            edges = [(
                edge["from"],
                edge["to"],
                edge["attrs"]
                ) for edge in data["Edges"]]
        G.add_edges_from(edges)
        
        def relabel(label:str):
            if(label.startswith("(")):
                return f"({label.split('/')[-1]}"
            else:
                return label.split('/')[-1]
        new_G = nx.relabel_nodes(G, {node:relabel(node) for node in G.nodes()})
        return new_G
    
    def _entry_exit(self):
        nodes = self.nodes(data=True)
        
        entry_points = []
        exit_points = []
        
        for node, data in nodes:
            if self.in_degree(node) == 0:
                entry_points.append(node)
            elif self.out_degree(node) == 0:
                exit_points.append(node)
        
        return (entry_points, exit_points)
    
    def _to_simple_paths(self):
        _g = deepcopy(self)
        
        tmp_root = "root--func%$+"
        
        entries, _ = self._entry_exit()
        if len(entries) > 1:
            self.add_node(tmp_root)
            for ent in entries:
                self.add_edge(tmp_root, ent)
                
        
        def remove_cycles(node:str, _parents:dict):
            outs = list(_g.out_edges(node))
            parents = _parents.copy()
            parents[node] = True
            
            if len(outs) == 0:
                return
            
            for _from,_to in outs:
                if parents.get(_to, False):
                    _g.remove_edge(_from, _to)
                    remove_cycles(node,parents)
                else:
                    remove_cycles(_to, parents)
            return
        
        root = next(nx.topological_sort(_g))
        remove_cycles(root,{})
        
        if len(entries) > 1:
            self.remove_node(tmp_root)
        return _g
    
    def get_feature_matrix(self) -> "OHCGraph":
        simpleG = self._to_simple_paths()
        entries, exits = simpleG._entry_exit()
        paths = {}
        idx = 1
        print(entries, exits)
        for ent in entries:
            for ext in exits:
                simple_paths = list(nx.all_simple_paths(simpleG, ent, ext))
                if not simple_paths:
                    continue
                paths[f'path{idx}'] = {fn:1 for fn in simple_paths[0]}
                idx+=1
        fm = pd.DataFrame(paths, dtype='Int64').fillna(0).transpose()
        return fm
        
    
    def show(self):
        plt.cla()
        nx.draw_circular(self,with_labels=True)
        plt.show()


