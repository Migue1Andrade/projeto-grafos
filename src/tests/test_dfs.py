import pytest
from src.graphs.algorithms import dfs

def test_dfs():
    graph = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['E'],
        'D': [],
        'E': []
    }
    result = dfs(graph, 'A')
    assert result == ['A', 'C', 'E', 'B', 'D']
