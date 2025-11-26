import pytest
from src.graphs.algorithms import bellman_ford

def test_bellman_ford_distancias_positivas():
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('C', 2), ('D', 5)],
        'C': [('D', 1)],
        'D': []
    }

    result = bellman_ford(graph, 'A')

    assert result == {
        'A': 0,
        'B': 1,
        'C': 3,
        'D': 4
    }


def test_bellman_ford_pesos_negativos_sem_ciclo():
    graph = {
        'A': [('B', 2), ('C', 5)],
        'B': [('C', -1)],
        'C': []
    }

    result = bellman_ford(graph, 'A')

    assert result['A'] == 0
    assert result['B'] == 2
    assert result['C'] == 1


def test_bellman_ford_ciclo_negativo():
    graph_neg = {
        'A': [('B', 1)],
        'B': [('C', -2)],
        'C': [('A', -1)]
    }

    with pytest.raises(ValueError):
        bellman_ford(graph_neg, 'A')