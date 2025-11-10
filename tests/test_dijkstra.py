import pytest
from src.graphs.algorithms import dijkstra

def test_dijkstra():
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('C', 2), ('D', 5)],
        'C': [('D', 1)],
        'D': []
    }
    result = dijkstra(graph, 'A')
    assert result == {'A': 0, 'B': 1, 'C': 3, 'D': 4}
