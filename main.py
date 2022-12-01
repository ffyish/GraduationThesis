import pickle
from pprint import pp

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage

from agglo import AgglomerativeClustering
from digraph import OHCGraph

f = open("rclone.json","r")
# pd.set_option('display.max_columns', None)
print("START LOADING....")
G = OHCGraph.load_json(f, attrs=False)
print("START FEATURE MATRIX")
fm = G.get_feature_matrix()
print("FM DONE")
# print("START AHC")
# cg_model = AgglomerativeClustering(fm)
# print("AHC DONE")
# with open("CGMODEL.pk", 'wb') as cgf:
#     pickle.dump(G, cgf)
#     print("SAVE CG...")
    
    
# with open("AHCMODEL.pk", 'wb') as pkf:
#     pickle.dump(cg_model, pkf)
#     print("DONE!")


# PKGS=$(go list ./... | grep `go list`/ | xargs | tr ' ' ,) && ./go-callvis -focus "" -limit "${PKGS}" `go list`

