from pprint import pp

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage

from agglo import AgglomerativeClustering
from digraph import OHCGraph

f = open("sample.json","r")
ff = open("booksampl.json", "r")

# pd.set_option('display.max_columns', None)
G = OHCGraph.load_json(f, as_id=False)
fm = G.get_feature_matrix()


def print_childs(c):
    if c.childs:
        return {"label":c.label, "childs":[print_childs(child) for child in c.childs]}
    else:
        return {"label":c.label, "childs":[]}


# X = np.random.rand(15,12)
# d = np.array([[1,2],[2,3]])
# fig = ff.create_dendrogram(d)
# fig.show()
# print(X)
ahc = AgglomerativeClustering(fm).create()
ahc.show()
print("Done")
# pp(print_childs(ahc))
# print(fm)
# 2/4
# 1/5

