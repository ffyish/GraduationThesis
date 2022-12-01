import networkx as nx
import ujson

from .base import BaseGraph


class StaticGraph(BaseGraph):
    @classmethod
    def load_json(cls, f, attrs=False) -> "BaseGraph":
        gdata = ujson.load(f)
