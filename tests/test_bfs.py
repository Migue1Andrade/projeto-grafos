import pytest
from src.graphs.algorithms import bfs

def test_bfs():
    graph = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['E'],
        'D': [],
        'E': []
    }

    ordem, camadas = bfs(graph, 'A')

    assert ordem == ['A', 'B', 'C', 'D', 'E']

    assert camadas == {
        'A': 0,
        'B': 1,
        'C': 1,
        'D': 2,
        'E': 2
    }
