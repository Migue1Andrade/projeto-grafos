import pytest
from src.graphs.algorithms import bellman_ford

def test_bellman_ford():
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('C', 2), ('D', 5)],
        'C': [('D', 1)],
        'D': []
    }
    result = bellman_ford(graph, 'A')
    assert result == {'A': 0, 'B': 1, 'C': 3, 'D': 4}

    # Testa ciclo negativo
    graph_neg = {
        'A': [('B', 1)],
        'B': [('C', -2)],
        'C': [('A', -1)]
    }
    try:
        bellman_ford(graph_neg, 'A')
        assert False, "Deveria lançar exceção de ciclo negativo"
    except ValueError:
        pass
