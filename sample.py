    #importing the package
import random

import matplotlib.pyplot as plt
import networkx as nx

nodes = 30
G = nx.scale_free_graph(nodes)
pos = nx.kamada_kawai_layout(G)
nx.draw(G, with_labels=False, node_size=100, pos=pos)
plt.savefig('plotgraph.png', dpi=300, with_labels=False)
plt.show()
