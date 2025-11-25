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
    result = bfs(graph, 'A')
    assert result == ['A', 'B', 'C', 'D', 'E']
